from typing import TypedDict, List, Dict, Any, Optional

class ResearchAgentState(TypedDict):
    """
    Represents the state of the research agent workflow.

    This state is passed between different nodes in the LangGraph, carrying
    information about the product, search results, and generated insights.

    Attributes:
        product_title (str): The name or short title of the product being researched.
        product_description (str): A brief description of what the product does.
        current_query (Optional[str]): The most recent search query generated.
        query_history (List[str]): A list of all previously attempted search queries.
        retry_count (int): The number of times the agent has retried due to hallucination.
        competitors_data (Optional[List[Dict[str, Any]]]): Raw data for identified 
            competitors fetched from the internet.
        hallucination_check (Optional[str]): A string indicating if the search results 
            are relevant or if any hallucination was detected.
        instructions (Optional[str]): The detailed competitor analysis and instructions 
            prepared for the report agent.
        final_response (Optional[Dict[str, Any]]): The final structured output 
            containing the analyzed research data.
    """
    product_title: str
    product_description: str
    current_query: Optional[str]
    query_history: List[str]
    retry_count: int
    competitors_data: Optional[List[Dict[str, Any]]]
    hallucination_check: Optional[str]
    instructions: Optional[str]
    final_response: Optional[Dict[str, Any]]
