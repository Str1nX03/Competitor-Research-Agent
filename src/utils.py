import os
import sys
from langchain_groq import ChatGroq
from src.exception import CustomException
from ddgs import DDGS

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
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=temperature
        )

        return llm

    except Exception as e:
        
        raise CustomException(e, sys)

def fetch_data(query: str, max_results: int = 5) -> list:
    """
    Fetches real-time search results from the internet using DuckDuckGo (ddgs).

    This function uses the `ddgs` module to perform a web search and returns 
    a list of dictionaries containing search results (title, href, body).

    Args:
        query (str): The search query string.
        max_results (int, optional): The maximum number of search results to return. 
            Defaults to 5.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'title': The title of the search result.
            - 'href': The URL of the search result.
            - 'body': A snippet or description of the result.

    Raises:
        CustomException: If there's an error during the search process.

    Example:
        ```python
        from src.utils import fetch_data
        results = fetch_data("Latest news on LangChain", max_results=3)
        for res in results:
            print(f"Title: {res['title']}\nLink: {res['href']}\n")
        ```
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
        
        return results

    except Exception as e:
        raise CustomException(e, sys)

