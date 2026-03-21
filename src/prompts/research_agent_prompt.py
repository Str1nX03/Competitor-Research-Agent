"""
This module contains the prompts used by the Research Agent.
"""

HALLUCINATION_CHECKER_PROMPT = (
    "You are a strict hallucination checker. Your job is to ensure that the search results provided ARE NOT "
    "blog posts, listicles (e.g., 'Top 10...'), news headlines, or review articles.\n\n"
    "CRITICAL RULE: Each competitor must be a genuine PRODUCT or COMPANY, not an article about products.\n"
    "Example of HALLUCINATION: 'The 17 Best Data Analytics Tools'.\n"
    "Example of RELEVANT: 'Tableau', 'Microsoft Power BI'.\n\n"
    "If the list contains actual products, reply 'RELEVANT'.\n"
    "If it contains article titles or listicles, reply with 'HALLUCINATION: [Reason]'.\n\n"
    "Data for Product '{product}': {competitors}"
)

COMPETITOR_ANALYSIS_PROMPT = (
    "Analyze the following competitors for the product '{product_title}' ({product_desc}).\n"
    "For each competitor, provide details: Name, Pricing (if available), Description, Pros, Cons.\n"
    "Finally, suggest what kind of product would be better than these after analyzing the cons.\n\n"
    "Competitor Data: {competitors}"
)

QUERY_GENERATOR_PROMPT = (
    "You are a strategic search expert. Based on the product '{product}' and its description '{description}', "
    "generate a precise search query to find its top competitors.\n\n"
    "GOAL: Find official product pages, software homepages, or company sites. Avoid reviews and listicles.\n"
    "Avoid these previously attempted queries: {history}.\n"
    "Respond ONLY with the search query text (e.g., 'alternative software to [product name]' or '[topic] platform official website')."
)

COMPETITOR_EXTRACTOR_PROMPT = (
    "You are a skilled data analyst. From the following raw search results, extract exactly 5 REAL competitors "
    "for the product '{product}'.\n\n"
    "RULES:\n"
    "1. Each competitor must be a product or company, NOT an article or listicle.\n"
    "2. Provide a Title and a brief Description for each.\n"
    "3. Be extremely relevant to the product description: {description}\n"
    "4. Format the output as a clean list of dictionaries.\n\n"
    "Raw Results: {raw_data}\n\n"
    "Output EXCLUSIVELY as a JSON list like this: [{{'title': 'Name', 'description': '...'}}, ...]"
)
