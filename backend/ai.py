from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )


def role_based_ai(role: str, message: str, context: str = ""):
    llm = get_llm()

    prompt = f"""
    You are a professional medical AI assistant.

    User Role: {role}

    Context:
    {context}

    Question:
    {message}
    """

    response = llm.invoke(prompt)
    return response.content