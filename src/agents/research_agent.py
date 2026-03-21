import sys
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from src.graph.state import ResearchAgentState
from src.utils import get_llm, fetch_data
from src.exception import CustomException
from src.prompts.research_agent_prompt import (
    HALLUCINATION_CHECKER_PROMPT, 
    QUERY_GENERATOR_PROMPT
)

class ResearchAgent:
    """
    An agent that performs competitor research using LangGraph.

    This agent automates the process of finding competitors for a product,
    validating the found data, and structured analysis of the competitive landscape.

    Attributes:
        llm (ChatGroq): The language model instance used for analysis and validation.
        graph (CompiledGraph): The compiled LangGraph workflow.
    """
    def __init__(self):
        """
        Initializes the ResearchAgent with an LLM and a compiled graph.

        Raises:
            CustomException: If initialization of LLM or graph building fails.
        """
        try:
            self.llm = get_llm()
            self.graph = self._build_graph()
        except Exception as e:
            raise CustomException(e, sys)

    def _build_graph(self):
        """
        Constructs and compiles the LangGraph workflow.

        The workflow follows this path:
        START -> generate_query -> internet_data -> checking_hallucination
        checking_hallucination -> END (if relevant)
        checking_hallucination -> generate_query (if retry < 3)
        checking_hallucination -> ERROR (if retry >= 3)

        Returns:
            CompiledGraph: The ready-to-use graph for the research process.

        Raises:
            CustomException: If any error occurs while building or compiling the graph.
        """
        try:
            workflow = StateGraph(ResearchAgentState)

            # Define nodes
            workflow.add_node("generate_query", self._generate_query)
            workflow.add_node("internet_data", self._internet_data)
            workflow.add_node("checking_hallucination", self._checking_hallucination)

            # Define edges
            workflow.add_edge(START, "generate_query")
            workflow.add_edge("generate_query", "internet_data")
            workflow.add_edge("internet_data", "checking_hallucination")
            
            # Conditional edge from checking_hallucination
            workflow.add_conditional_edges(
                "checking_hallucination",
                self._should_continue,
                {
                    "continue": END,
                    "retry": "generate_query"
                }
            )

            return workflow.compile()
        except Exception as e:
            raise CustomException(e, sys)

    def _generate_query(self, state: ResearchAgentState) -> Dict[str, Any]:
        """
        Node to generate a customized search query based on product details.

        Args:
            state (ResearchAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: A dictionary containing the generated 'current_query'.
        """
        try:
            prompt = QUERY_GENERATOR_PROMPT.format(
                product=state.get("product_title"),
                description=state.get("product_description"),
                history=", ".join(state.get("query_history", []))
            )
            response = self.llm.invoke(prompt)
            query = response.content.strip()
            
            return {"current_query": query}
        except Exception as e:
            raise CustomException(e, sys)

    def _internet_data(self, state: ResearchAgentState) -> Dict[str, Any]:
        """
        Node to fetch competitor data from the internet using the generated query.

        Args:
            state (ResearchAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: A dictionary containing fetched 'competitors_data' and updated history.

        Raises:
            CustomException: If data fetching fails.
        """
        try:
            query = state.get("current_query")
            history = state.get("query_history", [])
            
            raw_results = fetch_data(query, max_results=5)
            
            history.append(query)
            
            return {
                "competitors_data": raw_results,
                "query_history": history
            }
        except Exception as e:
            raise CustomException(e, sys)

    def _checking_hallucination(self, state: ResearchAgentState) -> Dict[str, Any]:
        """
        Node to validate fetched data relevance and track retries.

        Args:
            state (ResearchAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: A dictionary containing the 'hallucination_check' result 
                and updated 'retry_count'.

        Raises:
            CustomException: If the validation process fails.
        """
        try:
            competitors = state.get("competitors_data")
            product = state.get("product_title")
            retry_count = state.get("retry_count", 0)
            
            prompt = HALLUCINATION_CHECKER_PROMPT.format(
                product=product,
                competitors=competitors
            )
            
            response = self.llm.invoke(prompt)
            result = response.content.upper()
            
            # Increment retry count if hallucination detected
            new_retry_count = retry_count
            if "RELEVANT" not in result:
                new_retry_count += 1
                logging.warning(f"Hallucination detected. Retry {new_retry_count}/3. Reason: {result}")

            return {
                "hallucination_check": result,
                "retry_count": new_retry_count
            }
        except Exception as e:
            raise CustomException(e, sys)

    def _should_continue(self, state: ResearchAgentState) -> str:
        """
        Conditional edge logic to determine the next step in the workflow.

        Args:
            state (ResearchAgentState): The current state of the agent.

        Returns:
            str: The name of the next edge to follow ("continue", "retry").

        Raises:
            CustomException: If the maximum number of retries (3) is reached.
        """
        check_result = state.get("hallucination_check", "")
        retry_count = state.get("retry_count", 0)

        if "RELEVANT" in check_result:
            return "continue"
        
        if retry_count < 3:
            return "retry"
        
        raise CustomException(
            f"Max retries reached (3/3). Agent failed to find relevant data. "
            f"Last Reason: {check_result}",
            sys
        )

    def run(self, product_title: str, product_description: str):
        """
        Executes the research agent workflow for a given product with retry logic.

        Args:
            product_title (str): The name of the product.
            product_description (str): A brief description of the product.

        Returns:
            Dict[str, Any]: The final structured research analysis.

        Raises:
            CustomException: If graph execution fails or max retries exceeded.
        """
        try:
            inputs = {
                "product_title": product_title,
                "product_description": product_description,
                "query_history": [],
                "retry_count": 0
            }
            result = self.graph.invoke(inputs)
            return result
        except Exception as e:
            raise CustomException(e, sys)
