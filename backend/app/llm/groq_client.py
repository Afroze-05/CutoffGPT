from langchain_groq import ChatGroq
from ..config.config import settings

def get_groq_llm(model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature
    )
