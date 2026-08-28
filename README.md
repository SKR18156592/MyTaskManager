# 🧠 MyTaskManager

### A Stateful AI Task Management Agent with Long-Term Memory

MyTaskManager is an **LLM-powered task management agent** built with **LangGraph** that maintains structured user memory across conversations.

Instead of treating every conversation as an isolated interaction, MyTaskManager can remember important information about the user, manage tasks, and retain user-specific instructions. This enables more **personalized, context-aware, and stateful interactions**.

The project demonstrates how **LLMs, LangGraph workflows, structured memory, tool calling, and schema validation** can be combined to build a practical memory-enabled AI agent.

---

## 🚀 Key Features

* 🧠 **Long-Term Memory** — Maintains useful information across conversations.
* 💬 **Short-Term Conversational State** — Preserves context within a conversation thread.
* 👤 **Profile Memory** — Stores structured information about the user.
* ✅ **Task Memory** — Creates and manages structured to-do items.
* ⚙️ **Instruction Memory** — Remembers user-specific instructions and preferences for how tasks should be handled.
* 🔀 **Conditional Agent Routing** — Uses LangGraph to dynamically route memory operations.
* 🧩 **Structured Memory Extraction** — Uses Pydantic schemas for structured information.
* 🔄 **Memory Updating** — Updates existing memories instead of treating every interaction as a new memory.
* 🛠️ **Tool-Based Memory Management** — Allows the LLM to determine when a memory operation is required.
* 🔁 **Cyclic Agent Workflow** — Updates memory and returns control to the agent for continued reasoning.

---

# 🏗️ System Architecture

```text
                          ┌─────────────────┐
                          │      User       │
                          └────────┬────────┘
                                   │
                                   ▼
                        ┌────────────────────┐
                        │   MyTaskManager    │
                        │     LangGraph      │
                        └─────────┬──────────┘
                                  │
                       ┌──────────┴───────────┐
                       │                      │
                       ▼                      ▼
                Retrieve Memory          User Request
                       │                      │
            ┌──────────┼──────────┐           │
            │          │          │           │
            ▼          ▼          ▼           │
         Profile      ToDo   Instructions     │
            │          │          │           │
            └──────────┼──────────┘           │
                       │                      │
                       └──────────┬───────────┘
                                  ▼
                           ┌───────────────┐
                           │      LLM      │
                           │    Reasoning  │
                           └───────┬───────┘
                                   │
                          Memory Update Required?
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
                Profile          ToDo       Instructions
                 Update         Update          Update
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                         ┌────────────────────┐
                         │ Structured Memory  │
                         │     Update         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                           ┌──────────────┐
                           │MyTaskManager │
                           └──────┬───────┘
                                  │
                                  ▼
                            Final Response
```

---

# 🧠 Memory Architecture

A key design principle of MyTaskManager is the separation between **short-term conversational state** and **long-term user memory**.

```text
                     MyTaskManager
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       Short-Term State          Long-Term Memory
              │                         │
              ▼                 ┌───────┼────────┐
       Conversation          Profile   ToDo   Instructions
```

## Short-Term State

Short-term state contains information required to maintain the current conversational flow.

It is associated with the current LangGraph thread/conversation.

## Long-Term Memory

Long-term memory contains information that can remain useful beyond the current conversation.

MyTaskManager separates this information into different memory categories:

```text
Profile
ToDo
Instructions
```

This separation makes memory easier to reason about, update, and retrieve.

---

# 👤 1. Profile Memory

Profile memory stores relatively stable information about the user.

Examples include:

```text
Name
Location
Job
Interests
Connections
```

A structured schema allows the agent to represent this information consistently.

Example:

```python
class Profile(BaseModel):
    name: Optional[str]
    location: Optional[str]
    job: Optional[str]
    connections: list[str]
    interests: list[str]
```

---

# ✅ 2. To-Do Memory

To-do memory represents actionable tasks and their current state.

A task can contain:

```text
Task
Time to complete
Deadline
Possible solutions
Status
```

Supported task states include:

```text
not started
in progress
done
archived
```

Example:

```text
Task:
Complete RAG project

Deadline:
Friday

Status:
in progress
```

This allows the agent to maintain task context across conversations.

---

# ⚙️ 3. Instruction Memory

Instruction memory captures **how the user wants the agent to behave**.

For example:

```text
"When I create a large task, break it into smaller subtasks."
```

This differs from profile memory.

```text
Profile Memory
    ↓
Facts about the user

To-Do Memory
    ↓
Things the user needs to accomplish

Instruction Memory
    ↓
How the agent should behave
```

This separation allows MyTaskManager to personalize its behavior over time.

---

# 🔄 Agent Workflow

The main agent follows a cyclic workflow.

### Step 1 — Receive user input

```text
User
 ↓
LangGraph Agent
```

The agent receives the user's message along with relevant conversational context.

### Step 2 — Retrieve relevant memory

The agent accesses the user's stored memory categories:

```text
Profile
ToDo
Instructions
```

The retrieved information becomes additional context for the LLM.

### Step 3 — LLM reasoning

The LLM determines what should happen next.

Conceptually:

```text
                     User Message
                          │
                          ▼
                         LLM
                          │
                 ┌────────┴────────┐
                 │                 │
                 ▼                 ▼
          No memory update    Memory update
                 │                 │
                 ▼                 ▼
               Reply          Determine type
                                  │
                           ┌──────┼──────┐
                           ▼      ▼      ▼
                        Profile  ToDo  Instructions
```

### Step 4 — Conditional routing

LangGraph routes the request to the appropriate memory-update node.

```text
Memory Decision
      │
      ├── profile ───────► Profile Update
      │
      ├── todo ──────────► ToDo Update
      │
      └── instructions ─► Instruction Update
```

### Step 5 — Update structured memory

The selected memory is updated using structured schemas rather than storing arbitrary unstructured text.

### Step 6 — Return to the agent

After the memory operation completes, the workflow returns to the main agent.

```text
Memory Update
      │
      ▼
Main Agent
      │
      ▼
Final Response
```

This cyclic structure allows the agent to incorporate the newly updated memory into its subsequent reasoning.

---

# 🧩 Structured Memory with Pydantic

MyTaskManager uses **Pydantic models** to define the structure of stored information.

This provides:

* Schema validation
* Consistent data representation
* Predictable LLM outputs
* Easier memory updates
* Better downstream processing

Instead of relying entirely on free-form text:

```text
"Suman is interested in AI and has a project."
```

the system can represent information through structured fields.

```text
Profile
├── name
├── location
├── job
├── interests
└── connections
```

---

# 🔀 Why LangGraph?

A simple LLM application follows:

```text
User → LLM → Response
```

This becomes difficult when an application needs:

* State
* Memory
* Conditional routing
* Tool calls
* Multiple processing stages
* Iterative workflows

LangGraph allows these operations to be represented explicitly as a stateful graph.

```text
             ┌──────────────┐
             │     Agent    │
             └──────┬───────┘
                    │
                    ▼
               Decision Node
                    │
             ┌──────┼──────┐
             ▼      ▼      ▼
          Profile  ToDo  Instructions
             │      │      │
             └──────┼──────┘
                    ▼
                  Agent
```

This makes the workflow easier to extend and debug.

---

# 🛠️ Technology Stack

| Technology                  | Role                                     |
| --------------------------- | ---------------------------------------- |
| **Python**                  | Core implementation                      |
| **LangGraph**               | Stateful agent orchestration             |
| **LangChain**               | LLM application framework                |
| **OpenAI**                  | Large Language Model                     |
| **Pydantic**                | Structured schemas and validation        |
| **Trustcall**               | Structured memory extraction and updates |
| **LangGraph Checkpointing** | Short-term conversational state          |
| **LangGraph Store**         | Long-term memory                         |
| **Jupyter Notebook**        | Development and experimentation          |

---

# 📂 Project Structure

```text
MyTaskManager/
│
├── mytaskmanager.ipynb
├── README.md
└── .gitignore
```

The primary implementation is currently provided in:

```text
mytaskmanager.ipynb
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/SKR18156592/MyTaskManager.git
cd MyTaskManager
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install langchain langgraph langchain-openai trustcall pydantic
```

## 4. Configure the API key

Set your OpenAI API key as an environment variable.

### macOS / Linux

```bash
export OPENAI_API_KEY="your-api-key"
```

### Windows

```powershell
setx OPENAI_API_KEY "your-api-key"
```

**Never commit API keys or `.env` files containing secrets to GitHub.**

## 5. Run the notebook

Open:

```text
mytaskmanager.ipynb
```

using Jupyter Notebook, JupyterLab, or VS Code.

Run the cells sequentially to initialize the agent and interact with MyTaskManager.

---

# 💬 Example Interaction

### Conversation 1

```text
User:
My name is Suman and I'm preparing for an AI Engineer role.
```

The agent can identify relevant profile information and store it as structured memory.

### Conversation 2

```text
User:
Add "finish my RAG project" to my tasks.
```

The agent can create a structured to-do item.

### Conversation 3

```text
User:
Whenever I have a large task, break it into smaller subtasks.
```

The agent can store this as an instruction.

### Future Conversation

```text
User:
What should I work on today?
```

The agent can use previously stored task and user context to provide a personalized response.

---

# 🎯 What This Project Demonstrates

MyTaskManager demonstrates practical implementation of:

* Large Language Models
* AI Agents
* Stateful AI workflows
* LangGraph
* LangChain
* Long-term memory
* Short-term conversational state
* Structured memory
* Pydantic schemas
* Tool calling
* Conditional routing
* Memory extraction
* Memory updating
* Personalized AI assistants
* Agentic workflow design

---

# 🔬 Design Principles

### 1. State ≠ Memory

Short-term conversation state and long-term user memory serve different purposes.

```text
Short-Term State
      ↓
Current conversation

Long-Term Memory
      ↓
Information useful across conversations
```

### 2. Structured Memory > Raw Conversation History

Rather than repeatedly passing the entire conversation history to the LLM, useful information can be extracted into structured memory.

```text
Conversation
     │
     ▼
Information Extraction
     │
     ▼
Structured Memory
     │
     ▼
Future Retrieval
```

### 3. LLM Reasoning + Deterministic Workflow

The LLM handles semantic reasoning while LangGraph controls the execution flow.

```text
LLM
 ↓
Decide
 ↓
LangGraph
 ↓
Route
 ↓
Execute Memory Operation
```

This separation makes the overall system more controllable.

---

# 📈 Future Improvements

The current architecture provides a foundation for a more production-oriented memory system.

Planned improvements include:

### 🔹 Persistent Storage

Move beyond an in-memory development store toward persistent storage.

```text
In-Memory Store
      ↓
Production Database
```

### 🔹 Semantic Memory Retrieval

For larger memory collections, introduce embedding-based retrieval.

```text
User Query
    ↓
Embedding
    ↓
Vector Search
    ↓
Relevant Memories
    ↓
LLM
```

### 🔹 Hybrid Retrieval

Combine semantic retrieval with lexical retrieval for better recall.

```text
                 Query
                   │
           ┌───────┴───────┐
           ▼               ▼
     Semantic Search   Keyword Search
           │               │
           └───────┬───────┘
                   ▼
                Reranking
                   │
                   ▼
             Relevant Memory
```

### 🔹 Memory Deduplication

Detect whether newly extracted information already exists before creating another memory.

### 🔹 Conflict Resolution

Handle contradictory information.

```text
Existing:
Location = Delhi

New:
Location = Bengaluru
```

The memory system should determine whether the new information supersedes the old information.

### 🔹 Memory Importance

Classify memories according to their usefulness:

```text
High Importance
Medium Importance
Low Importance
Temporary
```

This can prevent unnecessary information from accumulating.

### 🔹 Memory Expiration

Some memories become stale and should eventually be removed or updated.

Examples:

```text
Temporary deadline
Current project
Short-term preference
```

### 🔹 Evaluation

A production-grade memory system should be evaluated using metrics such as:

```text
Memory Extraction Accuracy
Memory Update Accuracy
Memory Retrieval Precision
Memory Retrieval Recall
Duplicate Memory Rate
Conflict Resolution Accuracy
Latency
Token Usage
```

---

# 🌟 Why MyTaskManager?

Most basic LLM applications follow:

```text
Prompt → LLM → Response
```

MyTaskManager explores a more capable architecture:

```text
User
 │
 ▼
Stateful Agent
 │
 ├── Reason
 ├── Retrieve Memory
 ├── Decide
 ├── Update Memory
 └── Respond
 │
 ▼
Personalized Interaction
```

The goal is to move from a **stateless chatbot** toward a **memory-enabled AI agent** capable of maintaining useful context over time.

---

# 👨‍💻 Author

### Suman Kumar Raj

M.Tech — IIT Kharagpur

Interested in:

* Artificial Intelligence
* Machine Learning
* Generative AI
* Large Language Models
* AI Agents
* Retrieval-Augmented Generation
* Agent Memory Systems

---

# ⭐ Repository

**GitHub:**
https://github.com/SKR18156592/MyTaskManager

If you find the project useful, consider giving it a ⭐.

---

## 📌 Project Summary

**MyTaskManager** is a LangGraph-based stateful AI task-management agent that combines **LLM reasoning, structured long-term memory, conditional workflow orchestration, and personalized user context** to create more capable conversational task management.
