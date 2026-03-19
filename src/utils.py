import os
import sys
import logging
from langchain_groq import ChatGroq
from src.logger import logging
from src.exception import CustomException

def get_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.0) -> ChatGroq:
    """
    Initializes and returns a Groq Chat model instance.
    
    This function sets up a connection to the Groq API using the provided API key
    from the environment variables (`GROQ_API_KEY`). It creates a `ChatGroq` object
    which can be used for LLM interactions.
    
    Args:
        model_name (str, optional): The name of the Groq model to use. 
            Defaults to 'llama-3.1-8b-instant'.
        temperature (float, optional): The temperature parameter for the LLM, 
            controlling the randomness of the output. Defaults to 0.0 (deterministic).
            
    Returns:
        ChatGroq: An instantiated ChatGroq model ready for inference.
        
    Raises:
        CustomException: If there's an error during the LLM initialization, 
            such as a missing API key or network issue.
            
    Example:
        ```python
        from src.utils import get_llm
        llm = get_llm(model_name="llama-3.1-8b-instant", temperature=0.7)
        response = llm.invoke("Hello, who are you?")
        print(response.content)
        ```
    """
    try:

        logging.info("Initializing Groq LLM")

        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=temperature
        )

        logging.info("Groq LLM initialized successfully")

        return llm

    except Exception as e:
        
        raise CustomException(e, sys)

