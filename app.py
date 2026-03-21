import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from src.agents.research_agent import ResearchAgent
from src.agents.report_agent import ReportAgent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ensure outputs directory exists
OUTPUTS_DIR = os.path.join(os.getcwd(), "outputs")
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/app')
def product_page():
    return render_template('product.html')

@app.route('/api/research', methods=['POST'])
def run_research():
    try:
        data = request.json
        title = data.get('title')
        description = data.get('description')

        if not title or not description:
            return jsonify({"error": "Missing title or description"}), 400

        # 1. Start Research Agent
        research_agent = ResearchAgent()
        research_output = research_agent.run(title, description)

        # 2. Start Report Agent with Research findings
        # research_output should contain competitors_data
        report_agent = ReportAgent()
        pdf_path = report_agent.run(research_output.get("competitors_data", []))

        # Return the filename relative to outputs dir
        filename = os.path.basename(pdf_path)
        return jsonify({"success": True, "pdf_url": f"/outputs/{filename}"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/outputs/<path:filename>')
def serve_outputs(filename):
    return send_from_directory(OUTPUTS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
