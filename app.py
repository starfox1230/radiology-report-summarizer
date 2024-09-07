import openai
from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Set your OpenAI API key here or from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to send text to GPT-4o-mini and get a summary
def get_summary(case_text):
    try:
        response = openai.completions.create(
            model="gpt-4o-mini",  # Using the latest syntax for completions
            prompt=f"Summarize the following case: {case_text}",
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error processing case: {str(e)}"

# Function to process multiple cases from the bulk input
def process_cases(bulk_text):
    summaries = []
    # Split the bulk input into individual cases based on "Case"
    cases = bulk_text.split("Case")
    for case in cases:
        if "Attending Report" in case and "Resident Report" in case:
            attending_report = case.split("Attending Report:")[1].split("Resident Report:")[0].strip()
            resident_report = case.split("Resident Report:")[1].strip()
            case_text = f"Attending Report: {attending_report}\n\nResident Report: {resident_report}"
            summary = get_summary(case_text)
            summaries.append(f"Case {cases.index(case)}:\n{summary}\n")
    return summaries

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    bulk_text = request.form['case_text']
    summaries = process_cases(bulk_text)
    summary_output = "\n".join(summaries)
    return render_template('index.html', case_text=bulk_text, summary=summary_output)

if __name__ == "__main__":
    app.run(debug=True)
