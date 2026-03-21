"""
This module contains the prompts used by the Research Agent.
"""

HALLUCINATION_CHECKER_PROMPT = (
    "You are a hallucination checker. Verify if the following competitor search results "
    "are relevant to the product '{product}'. If they are relevant, reply 'RELEVANT'. "
    "If they seem unrelated or hallucinated, describe why.\n\n"
    "Data: {competitors}"
)

COMPETITOR_ANALYSIS_PROMPT = (
    "Analyze the following competitors for the product '{product_title}' ({product_desc}).\n"
    "For each competitor, provide details: Name, Pricing (if available), Description, Pros, Cons.\n"
    "Finally, suggest what kind of product would be better than these after analyzing the cons.\n\n"
    "Competitor Data: {competitors}"
)

QUERY_GENERATOR_PROMPT = (
    "You are a search expert. Based on the product '{product}' and its description '{description}', "
    "generate a precise search query to find its top 5 competitors. "
    "Avoid these previously attempted queries: {history}. "
    "Respond ONLY with the search query text."
)
