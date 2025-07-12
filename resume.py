import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from dotenv import load_dotenv
import io
import re
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("YOUR_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)  

Model = genai.GenerativeModel("gemini-2.0-flash-lite") 

def extract_text_from_pdf(uploaded_file):
    """Yüklenen PDF dosyasından metni ayıklar."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return None

def analyzecv_pdf_withllm(text, report_language):
    prompt = f"""
You are a globally experienced HR and career evaluation expert with deep cross-industry insight. You will perform an extremely detailed, holistic analysis of the CV provided below. Go beyond numeric scoring — offer professional interpretation, inferences, and personalized guidance based on the profile.

GENERAL INSTRUCTIONS:
- Detect and report the actual language of the CV content.
- Regardless of the detected language, generate the entire report in the selected report language below.
- Respond in {report_language}.
- Be objective, professional, and constructive in tone.
- If certain sections are missing, infer from available information.
- Follow international career evaluation best practices.
- Ensure all scoring (0–100) is balanced and evidence-based. Do not give overly generous or overly harsh scores. Each score must reflect the content quality, quantity, and relevance in the CV.

* 1. LANGUAGE DETECTION
Identify the dominant language of the CV.

* 2. CAREER DOMAIN MATCHING
Identify the top 3 most suitable career domains for this candidate.
For each domain:
- Give a score out of 100
- Justify why the candidate fits that domain (based on experience, skills, education, etc.)
- Optionally mention related roles the candidate could consider

* 3. COMPETENCY EVALUATION
Evaluate the candidate across 10 dimensions. For each, give:
- A score out of 100
- Specific strengths and examples from the CV
- Observations or red flags (if any)

* 4. STRATEGIC INSIGHTS & INTERPRETATION
- Based on the full CV, what type of roles is this candidate most suited for now?
- What future roles could be targeted with slight improvements?
- Are there signs of underutilized potential?
- Does the profile indicate a specialist or generalist tendency?
- Are there inconsistencies or missing data that should be improved?

* 5. DEVELOPMENT RECOMMENDATIONS
Provide clear, practical and personalized suggestions for how the candidate can improve:
- Skills, certifications, degrees
- Portfolio, communication, network

* 6. COMPARATIVE BENCHMARKING (OPTIONAL)

* 7. OVERALL SUMMARY

Absolutely follow the JSON format shown below. Do not add any text, comments, or explanations outside the JSON structure.

{{
  "language": "The actual dominant language of the CV (not the report language)",
  "domain_scores": [
    {{"domain": "Domain Name", "score": 88, "justification": "Why this domain fits"}}
  ],
  "competency_scores": [
    {{"category": "Core Skills & Tools", "score": 85, "strength": "X", "observation": "Y"}}
  ],
  "strategic_insights": "Full paragraph insight",
  "development_recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "comparative_benchmarking": "Paragraph comparing this candidate with others",
  "overall_summary": {{
    "overall_score": 87,
    "key_strengths": ["Strength 1", "Strength 2"],
    "areas_to_improve": ["Weakness 1", "Weakness 2"],
    "talent_potential": "High / Moderate / Needs Development"
  }}
}}

CV Content:
{text}
"""
    try:
        response = Model.generate_content(prompt)
        raw_text = response.text
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            st.error("Sorry, the analysis could not be completed. Please try again later or upload a different file.")
            return None
        json_str = match.group(0)
        return json.loads(json_str)
    except Exception as e:
        st.error("An error occurred while processing your resume. Please try again or upload a different file.")
        return None

st.title("Advanced Resume Analysis Application")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    if text:
        # Language selector after PDF
        st.subheader("Select report language")
        language_options = ["English", "German", "French", "Italian", "Russian", "Turkish", "Spanish"]
        selected_language = st.selectbox("Choose a language for the report", language_options)

        # Trigger analysis
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing Resume..."):
                result = analyzecv_pdf_withllm(text, selected_language)
                if result:
                    st.subheader("Detected Language")
                    st.write(result.get("language", "Not detected"))

                    st.subheader("Career Domain Fit Scores")
                    domain_data = result.get("domain_scores", [])
                    if domain_data:
                        st.table([{ "Domain": d["domain"], "Score": d["score"], "Justification": d["justification"] } for d in domain_data])

                    st.subheader("Competency Evaluation")
                    comp_data = result.get("competency_scores", [])
                    if comp_data:
                        st.table([{ 
                            "Category": c["category"], 
                            "Score": c["score"], 
                            "Strength": c["strength"], 
                            "Observation": c["observation"] 
                        } for c in comp_data])

                    st.subheader("Strategic Insights")
                    st.write(result.get("strategic_insights", "N/A"))

                    st.subheader("Development Recommendations")
                    for rec in result.get("development_recommendations", []):
                        st.markdown(f"- {rec}")

                    st.subheader("Comparative Benchmarking")
                    st.write(result.get("comparative_benchmarking", "N/A"))

                    st.subheader("Overall Summary")
                    summary = result.get("overall_summary", {})
                    st.markdown(f"**Overall Score:** {summary.get('overall_score', 'N/A')}/100")
                    st.markdown("**Key Strengths:**")
                    for strength in summary.get("key_strengths", []):
                        st.markdown(f"- {strength}")
                    st.markdown("**Areas to Improve:**")
                    for area in summary.get("areas_to_improve", []):
                        st.markdown(f"- {area}")
                    st.markdown(f"**Talent Potential:** {summary.get('talent_potential', 'N/A')}")
