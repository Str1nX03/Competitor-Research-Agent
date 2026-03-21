import os
import sys
from typing import Dict, Any, List
from fpdf import FPDF
from langgraph.graph import StateGraph, START, END
from src.graph.state import ReportAgentState
from src.utils import get_llm, fetch_data
from src.exception import CustomException
from src.prompts.report_agent_prompt import (
    DEEP_RESEARCH_PROMPT, 
    REPORT_GENERATOR_PROMPT,
    REPORT_HALLUCINATION_CHECKER_PROMPT
)

class ReportAgent:
    """
    An agent that generates detailed competitor reports and exports them as PDF.

    Attributes:
        llm (ChatGroq): The language model instance.
        graph (CompiledGraph): The compiled LangGraph workflow.
    """
    def __init__(self):
        """
        Initializes the ReportAgent with an LLM and a compiled graph workflow.

        Raises:
            CustomException: If LLM initialization or graph construction fails.
        """
        try:
            self.llm = get_llm()
            self.graph = self._build_graph()
        except Exception as e:
            raise CustomException(e, sys)

    def _build_graph(self):
        """
        Constructs and compiles the LangGraph workflow for processing competitor data.

        The workflow follows:
        START -> internet_data -> generate_report -> get_pdf -> END

        Returns:
            CompiledGraph: The ready-to-use graph for generating reports.

        Raises:
            CustomException: If any error occurs while building or compiling the graph.
        """
        try:
            workflow = StateGraph(ReportAgentState)

            workflow.add_node("internet_data", self._internet_data)
            workflow.add_node("checking_hallucination", self._checking_hallucination)
            workflow.add_node("generate_report", self._generate_report)
            workflow.add_node("get_pdf", self._get_pdf)

            workflow.add_edge(START, "internet_data")
            workflow.add_edge("internet_data", "checking_hallucination")
            
            workflow.add_conditional_edges(
                "checking_hallucination",
                self._should_continue,
                {
                    "continue": "generate_report",
                    "retry": "internet_data"
                }
            )
            
            workflow.add_edge("generate_report", "get_pdf")
            workflow.add_edge("get_pdf", END)

            return workflow.compile()
        except Exception as e:
            raise CustomException(e, sys)

    def _internet_data(self, state: ReportAgentState) -> Dict[str, Any]:
        """
        Node to perform deep research on each competitor identifying company history and product dates.

        Args:
            state (ReportAgentState): The current state containing 'competitors_data'.

        Returns:
            Dict[str, Any]: Updates 'detailed_research' with fetched company/product information.

        Raises:
            CustomException: If research search or LLM invocation fails.
        """
        try:
            competitors = state.get("competitors_data", [])
            detailed_results = {}

            for comp in competitors:
                name = comp.get("title") or comp.get("name")
                description = comp.get("description") or ""
                
                query = f"history and launch date of company {name} and product {description}"
                search_results = fetch_data(query, max_results=5)
                
                prompt = DEEP_RESEARCH_PROMPT.format(
                    company_name=name,
                    product_name=description,
                    search_metadata=str(search_results)
                )
                
                response = self.llm.invoke(prompt)
                detailed_results[name] = response.content

            return {"detailed_research": detailed_results}
        except Exception as e:
            raise CustomException(e, sys)

    def _checking_hallucination(self, state: ReportAgentState) -> Dict[str, Any]:
        """
        Node to validate the deep research results for hallucinations or low quality listicles.

        Args:
            state (ReportAgentState): The current state containing 'detailed_research'.

        Returns:
            Dict[str, Any]: Updates 'hallucination_check' and 'retry_count'.

        Raises:
            CustomException: If validation fails.
        """
        try:
            research_data = state.get("detailed_research", {})
            retry_count = state.get("retry_count", 0)
            
            prompt = REPORT_HALLUCINATION_CHECKER_PROMPT.format(
                research_data=str(research_data)
            )
            
            response = self.llm.invoke(prompt)
            result = response.content.upper()
            
            new_retry_count = retry_count
            if "RELEVANT" not in result:
                new_retry_count += 1

            return {
                "hallucination_check": result,
                "retry_count": new_retry_count
            }
        except Exception as e:
            raise CustomException(e, sys)

    def _should_continue(self, state: ReportAgentState) -> str:
        """
        Conditional edge to determine if report generation should proceed or retry research.

        Args:
            state (ReportAgentState): The current state.

        Returns:
            str: "continue" or "retry".

        Raises:
            CustomException: If max retries are exceeded.
        """
        check_result = state.get("hallucination_check", "")
        retry_count = state.get("retry_count", 0)

        if "RELEVANT" in check_result:
            return "continue"
        
        if retry_count < 5:
            return "retry"
        
        return "continue"

    def _generate_report(self, state: ReportAgentState) -> Dict[str, Any]:
        """
        Node to synthesize all researched data into a professional markdown-formatted report.

        Args:
            state (ReportAgentState): The current state containing 'competitors_data' 
                and 'detailed_research'.

        Returns:
            Dict[str, Any]: Updates 'final_report' with the generated markdown content.

        Raises:
            CustomException: If report synthesis fails.
        """
        try:
            competitors = state.get("competitors_data", [])
            research = state.get("detailed_research", {})
            
            combined_data = []
            for comp in competitors:
                name = comp.get("title") or comp.get("name")
                combined_data.append({
                    "name": name,
                    "description": comp.get("description", ""),
                    "deep_details": research.get(name, "No details found."),
                    "pros": comp.get("pros", "N/A"),
                    "cons": comp.get("cons", "N/A")
                })

            prompt = REPORT_GENERATOR_PROMPT.format(data=str(combined_data))
            response = self.llm.invoke(prompt)
            
            return {"final_report": response.content}
        except Exception as e:
            raise CustomException(e, sys)

    def _get_pdf(self, state: ReportAgentState) -> Dict[str, Any]:
        """
        Node to convert the synthesized markdown report into a structured PDF file
        with enhanced styling (headers, colors, lines).

        Args:
            state (ReportAgentState): The current state containing 'final_report'.

        Returns:
            Dict[str, Any]: Updates 'pdf_path' with the location of the generated PDF.

        Raises:
            CustomException: If PDF generation or file writing fails.
        """
        try:
            content = state.get("final_report", "")
            pdf = FPDF()
            pdf.add_page()
            
            # Professional Colors
            teal_color = (31, 107, 131)
            dark_gray = (60, 60, 60)
            black = (0, 0, 0)

            lines = content.split('\n')
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    pdf.ln(4)
                    continue

                try:
                    # Header 1: # Executive Summary
                    if clean_line.startswith('# '):
                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 18)
                        pdf.set_text_color(*teal_color)
                        pdf.multi_cell(0, 12, clean_line[2:])
                        
                        # Add Horizontal Line
                        pdf.set_draw_color(*teal_color)
                        pdf.set_line_width(0.8)
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                        pdf.ln(8)
                    
                    # Header 2: ## Overview or similar
                    elif clean_line.startswith('## '):
                        pdf.ln(5)
                        pdf.set_font("Arial", "B", 15)
                        pdf.set_text_color(*teal_color)
                        pdf.multi_cell(0, 10, clean_line[3:])
                        pdf.ln(2)

                    # Header 3: ### 1. Competitor Name
                    elif clean_line.startswith('### '):
                        pdf.ln(3)
                        pdf.set_font("Arial", "B", 13)
                        pdf.set_text_color(*teal_color)
                        pdf.multi_cell(0, 10, clean_line[4:])
                        pdf.ln(1)
                    
                    # Bold labels like **Pros:**, **Cons:**, **Services:**
                    elif clean_line.startswith('**') and ':' in clean_line:
                        parts = clean_line.split(':', 1)
                        label = parts[0].replace('**', '').strip()
                        value = parts[1].replace('**', '').strip()
                        
                        pdf.set_font("Arial", "B", 11)
                        pdf.set_text_color(*black)
                        # We use 0 width but we must be careful with write/cell combo
                        # Better to just use one multi_cell with bold/regular if possible, 
                        # but fpdf2 multi_cell doesn't support mixed styles easily.
                        # We'll use a small cell for label and multi_cell for value.
                        pdf.set_font("Arial", "B", 11)
                        pdf.cell(pdf.get_string_width(f"{label}: ") + 2, 8, f"{label}: ")
                        pdf.set_font("Arial", "", 11)
                        pdf.set_text_color(*dark_gray)
                        pdf.multi_cell(0, 8, value)
                    
                    # Bullet points: - or *
                    elif clean_line.startswith('- ') or clean_line.startswith('* '):
                        pdf.set_font("Arial", "", 11)
                        pdf.set_text_color(*dark_gray)
                        # Indent bullet points
                        pdf.set_x(15)
                        text = clean_line[2:].replace('**', '')
                        pdf.multi_cell(0, 8, txt=f"• {text.encode('latin-1', 'replace').decode('latin-1')}")
                        pdf.set_x(10)
                    
                    # Standard text
                    else:
                        pdf.set_font("Arial", "", 11)
                        pdf.set_text_color(*black)
                        # More aggressive markdown cleanup
                        text = clean_line.replace('**', '').replace('*', '').replace('__', '')
                        pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
                
                except Exception as inner_e:
                    pdf.set_x(10) # Reset X on error
                    pdf.set_font("Arial", "", 11)
                    # Aggressive cleanup here too
                    text = clean_line.replace('**', '').replace('*', '')
                    pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))

            output_dir = "outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = os.path.join(output_dir, "Competitor_Report.pdf")
            pdf.output(filename)
            
            return {"pdf_path": filename}
        except Exception as e:
            raise CustomException(e, sys)

    def run(self, competitors_data: List[Dict[str, Any]]):
        """
        Main entry point to execute the report generation workflow.

        Args:
            competitors_data (List[Dict[str, Any]]): List of validated competitors 
                (usually from ResearchAgent output).

        Returns:
            str: The file path to the generated PDF report.

        Raises:
            CustomException: If the graph invocation or processing fails.
        """
        try:
            inputs = {
                "competitors_data": competitors_data,
                "detailed_research": {},
                "final_report": "",
                "pdf_path": "",
                "retry_count": 0,
                "hallucination_check": ""
            }
            result = self.graph.invoke(inputs)
            return result.get("pdf_path")
        except Exception as e:
            raise CustomException(e, sys)
