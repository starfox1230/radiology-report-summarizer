import openai
from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to send text to GPT-4o-mini and get a summary for a single pair of reports
def get_summary(case_text):
    try:
        # Use the new ChatCompletion.create method instead of Completion.create
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with gpt-4o-mini or another model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes radiology reports."},
                {"role": "user", "content": f"Succinctly organize the changes made by the attending to the resident's radiology reports into: 1) missed major findings, 2) missed minor findings, and 3) clarified descriptions of findings. The reports are: {case_text}"}
            ],
            max_tokens=1000,
            temperature=0  # Adjust if needed
        )
        # Return the text of the response
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error processing case: {str(e)}"

# Route to handle the form and bulk input
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    bulk_text = request.form['case_text']
    summaries = process_cases(bulk_text)
    
    # Join the summaries into a single string
    summary_output = "\n".join(summaries)
    
    return render_template('index.html', case_text=bulk_text, summary=summary_output)

# Function to process multiple cases from the bulk input
def process_cases(bulk_text):
    summaries = []
    
    # Split the bulk input into individual cases based on "Case"
    cases = bulk_text.split("Case")

    # Iterate through each case and process it
    for case in cases:
        if "Attending Report" in case and "Resident Report" in case:
            # Extract attending and resident reports
            attending_report = case.split("Attending Report:")[1].split("Resident Report:")[0].strip()
            resident_report = case.split("Resident Report:")[1].strip()

            # Create a comparison text for GPT-4o-mini
            case_text = f"Attending Report: {attending_report}\n\nResident Report: {resident_report}"

            # Get the summary from GPT-4o-mini
            summary = get_summary(case_text)

            # Add the summary to the results
            summaries.append(f"Case {cases.index(case) + 1}:\n{summary}\n")

    return summaries

if __name__ == "__main__":
    app.run(debug=True)
