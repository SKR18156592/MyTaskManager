from trustcall import create_extractor
from src.config import get_model
from src.schemas import Profile, ToDo

model = get_model()

profile_extractor = create_extractor(
    model,
    tools=[Profile],
    tool_choice="Profile"
)

todo_extractor = create_extractor(
    model,
    tools=[ToDo],
    tool_choice="ToDo",
    enable_inserts=True
)