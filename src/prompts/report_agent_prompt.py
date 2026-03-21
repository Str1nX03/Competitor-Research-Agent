"""
Prompts for the Report Agent.
"""

DEEP_RESEARCH_PROMPT = (
    "You are an elite corporate investigator. For the company '{company_name}' and its product '{product_name}', "
    "conduct a deep-dive research into the following:\n"
    "1. Comprehensive company history, including founding story and evolution.\n"
    "2. Exact product launch date and major version milestones.\n"
    "3. Market positioning, target audience, and unique selling propositions (USPs).\n"
    "4. Detailed financial milestones or recent news if available.\n\n"
    "Search Results Metadata: {search_metadata}\n\n"
    "Synthesize this into a rich, detailed summary of at least 300 words."
)

REPORT_GENERATOR_PROMPT = (
    "You are a master business analyst. Generate a concise, high-value competitor intelligence report.\n"
    "DO NOT use '**' or other markdown symbols for bolding inside your text.\n\n"
    "STRUCTURE:\n"
    "1. '# Market Overview': A brief 1-paragraph summary of the market and product popularity.\n"
    "2. '## Competitor Breakdown':\n"
    "For each competitor, use this EXACT format:\n"
    "### [Number]. [Product Name]\n"
    "**OVERVIEW:** [Exactly 3 lines describing product, company, and history]\n"
    "**PROS:**\n"
    "- [List of 2 to 4 bullet points]\n"
    "**CONS:**\n"
    "- [List of 2 to 4 bullet points]\n"
    "**MAJOR STRENGTH:** [Exactly 2 lines of analysis]\n"
    "**MAJOR LIMITATION:** [Exactly 2 lines of analysis]\n"
    "**TIPS TO OUTPERFORM:**\n"
    "- [List of 2 to 3 actionable tips]\n\n"
    "Historical Data: {data}\n\n"
    "Follow the line/bullet counts strictly. Be concise but insightful."
)

REPORT_HALLUCINATION_CHECKER_PROMPT = (
    "You are a deep-research validator. Check if the following research data for competitors "
    "contains specific company history and launch dates, OR if it's just generic article headlines.\n\n"
    "Data: {research_data}\n\n"
    "If the data is factual and specific to the companies, reply 'RELEVANT'.\n"
    "If it is generic news, listicles, or article titles, reply 'HALLUCINATION: [Reason]'."
)
