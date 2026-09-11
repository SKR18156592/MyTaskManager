import uuid
from datetime import datetime
from typing import Literal
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import merge_message_runs, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

from src.config import get_model
from src.schemas import UpdateMemory
from src.prompts import MODEL_SYSTEM_MESSAGE, TRUSTCALL_INSTRUCTION, CREATE_INSTRUCTIONS
from src.extractors import profile_extractor, todo_extractor
from src.utils import Spy, extract_tool_info

model = get_model()

def my_task_manager(state: MessagesState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]

    namespace = ("profile", user_id)
    memories = store.search(namespace)
    user_profile = memories[0].value if memories else None

    namespace = ("todo", user_id)
    memories = store.search(namespace)
    todo = "\n".join(f"{mem.value}" for mem in memories)

    namespace = ("instructions", user_id)
    memories = store.search(namespace)
    instructions = memories[0].value.get("memory", "") if memories else ""

    sys_msg = MODEL_SYSTEM_MESSAGE.format(
        user_profile=user_profile,
        todo=todo,
        instructions=instructions
    )

    response = model.bind_tools([UpdateMemory], parallel_tool_calls=False).invoke(
        [SystemMessage(content=sys_msg)] + state["messages"]
    )
    return {"messages": [response]}

def route_messages(state: MessagesState, config: RunnableConfig, store: BaseStore) -> Literal[END, "update_profile", "update_todos", "update_instructions"]:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END

    tool_call = last_message.tool_calls[0]
    update_type = tool_call["args"]["update_type"]
    if update_type == "user":
        return "update_profile"
    elif update_type == "todo":
        return "update_todos"
    elif update_type == "instructions":
        return "update_instructions"
    raise ValueError(f"Unknown update_type: {update_type}")

def update_profile(state: MessagesState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("profile", user_id)
    existing_items = store.search(namespace)

    existing_memories = [
        (existing_item.key, "Profile", existing_item.value) for existing_item in existing_items
    ] if existing_items else None

    formatted_instructions = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(merge_message_runs(
        messages=[SystemMessage(content=formatted_instructions)] + state["messages"][:-1]
    ))

    result = profile_extractor.invoke({
        "messages": updated_messages,
        "existing": existing_memories
    })

    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace, rmeta.get("json_doc_id", str(uuid.uuid4())), r.model_dump(mode="json"))

    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(content="updated_profile", tool_call_id=tool_calls[0]["id"])
        ]
    }

def update_todos(state: MessagesState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("todo", user_id)
    existing_items = store.search(namespace)

    existing_memories = [
        (existing_item.key, "ToDo", existing_item.value) for existing_item in existing_items
    ] if existing_items else None

    formatted_instructions = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(merge_message_runs(
        messages=[SystemMessage(content=formatted_instructions)] + state["messages"][:-1]
    ))

    spy = Spy()
    result = todo_extractor.with_listeners(on_end=spy).invoke({
        "messages": updated_messages,
        "existing": existing_memories
    })

    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace, rmeta.get("json_doc_id", str(uuid.uuid4())), r.model_dump(mode="json"))

    tool_calls = state["messages"][-1].tool_calls
    todo_update_msg = extract_tool_info(spy.called_tools, "ToDo")

    return {
        "messages": [
            ToolMessage(content=todo_update_msg, tool_call_id=tool_calls[0]["id"])
        ]
    }

def update_instructions(state: MessagesState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("instructions", user_id)
    existing_items = store.get(namespace, "user_instructions")

    sys_msg = CREATE_INSTRUCTIONS.format(
        current_instructions=existing_items.value.get("memory", "") if existing_items else None
    )
    new_memory = model.invoke(
        [SystemMessage(content=sys_msg)] + state["messages"][:-1] + [HumanMessage(content="Please update the instructions based on the conversation")]
    )

    store.put(namespace, "user_instructions", {"memory": new_memory.content})

    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(content="updated_instructions", tool_call_id=tool_calls[0]["id"])
        ]
    }

# Assemble Graph
builder = StateGraph(MessagesState)
builder.add_node("my_task_manager", my_task_manager)
builder.add_node("update_profile", update_profile)
builder.add_node("update_todos", update_todos)
builder.add_node("update_instructions", update_instructions)

builder.add_edge(START, "my_task_manager")
builder.add_conditional_edges("my_task_manager", route_messages)
builder.add_edge("update_profile", "my_task_manager")
builder.add_edge("update_todos", "my_task_manager")
builder.add_edge("update_instructions", "my_task_manager")

across_thread_memory = InMemoryStore()
within_thread_memory = MemorySaver()

task_manager_agent = builder.compile(
    checkpointer=within_thread_memory,
    store=across_thread_memory
)