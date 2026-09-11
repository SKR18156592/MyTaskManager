from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Memory(BaseModel):
    content: str = Field(
        description="The main content of the memory. For example: User expressed interest in learning about French."
    )

class MemoryCollection(BaseModel):
    memories: list[Memory] = Field(description="A list of memories about the user")

class Profile(BaseModel):
    """Profile representation of the user."""
    name: Optional[str] = Field(description="The user's name", default=None)
    location: Optional[str] = Field(description="The user's location", default=None)
    job: Optional[str] = Field(description="The user's job", default=None)
    connections: list[str] = Field(
        description="Personal connections of the user, such as family members, friends, or coworkers",
        default_factory=list
    )
    interests: list[str] = Field(
        description="Interests that the user has",
        default_factory=list
    )

class ToDo(BaseModel):
    """Task item representation."""
    task: str = Field(description="The task to be completed.")
    time_to_complete: Optional[int] = Field(description="Estimated time to complete the task (in minutes).")
    deadline: Optional[datetime] = Field(
        description="When the task needs to be completed by (if applicable)",
        default=None
    )
    solutions: list[str] = Field(
        description="List of specific, actionable solutions (e.g., specific ideas, service providers, or concrete options relevant to completing the task)",
        default_factory=list
    )
    status: Literal["not started", "in progress", "done", "archived"] = Field(
        description="Current status of the task",
        default="not started"
    )

class UpdateMemory(TypedDict):
    """Decision on what memory type to update."""
    update_type: Literal["user", "todo", "instructions"]