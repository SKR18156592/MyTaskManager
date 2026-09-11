import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = 0.0

def get_model():
    return ChatOpenAI(model=DEFAULT_MODEL, temperature=TEMPERATURE)