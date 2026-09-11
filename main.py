import sys
from langchain_core.messages import HumanMessage
from src.graph import task_manager_agent, across_thread_memory

def run_cli():
    print("=" * 60)
    print("🤖 MyTaskManager — LangGraph Long-Term Memory Agent")
    print("=" * 60)
    user_id = input("Enter user ID (e.g., Suman): ").strip() or "Suman"
    thread_id = input("Enter thread/session ID (default: 1): ").strip() or "1"
    config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

    print(f"\n[+] Active Session for: {user_id} | Thread: {thread_id}")
    print("Type your message or '/memories' to inspect store, '/quit' to exit.\n")

    while True:
        try:
            user_input = input(f"{user_id} > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("/quit", "exit"):
                print("Exiting.")
                break
            if user_input.lower() == "/memories":
                print(f"\n--- [Profile Memory: {user_id}] ---")
                for m in across_thread_memory.search(("profile", user_id)):
                    print(m.value)
                print(f"\n--- [ToDo List: {user_id}] ---")
                for m in across_thread_memory.search(("todo", user_id)):
                    print(m.value)
                print(f"\n--- [Custom Instructions: {user_id}] ---")
                for m in across_thread_memory.search(("instructions", user_id)):
                    print(m.value)
                print("-" * 40 + "\n")
                continue

            input_messages = [HumanMessage(content=user_input)]
            for chunk in task_manager_agent.stream({"messages": input_messages}, config, stream_mode="values"):
                last_msg = chunk["messages"][-1]
            
            # Print only final response
            print(f"\nAssistant > {last_msg.content}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    run_cli()