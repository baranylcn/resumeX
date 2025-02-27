import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from dotenv import load_dotenv
import io  

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
        st.error(f"PDF okuma hatası: {e}")
        return None


def analyzecv_pdf_withllm(text):
  
    prompt = f"""
You are a software engineering recruitment specialist. Analyze the CV provided below to assess the candidate's technical skills and experience.  

💡 **Important Notes:**  
- **Determine the language of the CV** and provide the analysis in **the same language**.  
- If the CV is entirely in **English**, respond in **English**. If it's in **Turkish**, respond in **Turkish**.  
- If the CV contains mixed languages, select the **most dominant language** and respond accordingly.  
- If some sections are missing, **analyze based on the available information**.  

---

### **1️. Software Domain Analysis**  
- Identify the **top 3 most suitable software domains** for the candidate.  
- Consider the **Summary, Cover Letter, Experience, Projects, and Education** sections when evaluating.  
- Assign scores **out of a total of 100 points** across the three domains.  

📌 **Table Format:**  
| Domain | Score |
|----------|------|
| Domain 1 | XX  |
| Domain 2 | XX  |
| Domain 3 | XX  |

---

### **2️. Technical and General Assessment**  
Evaluate the candidate's competencies based on the following criteria and **assign a score between 0 and 100**:  
- **Technical Skills:** Programming languages, frameworks, databases, cloud technologies  
- **Experience & Projects:** Work history, project roles, responsibilities  
- **Education & Certifications:** Degrees, bootcamps, certifications, academic achievements  
- **Problem-Solving Ability:** Algorithms, data structures, optimization skills  
- **Communication & Teamwork:** Technical documentation, collaboration, mentoring experience  
- **Open Source Contributions & Side Projects:** GitHub activity, contributions, independent projects  

📌 **Table Format:**  
| Criterion | Score |
|----------------------------|------|
| Technical Skills           | XX/100 |
| Experience & Projects      | XX/100 |
| Education & Certifications | XX/100 |
| Problem-Solving Ability    | XX/100 |
| Communication & Teamwork   | XX/100 |
| Open Source & Side Projects | XX/100 |

---

### **3️. Overall Evaluation**  
Assess the candidate's **overall performance out of 100 points** and summarize their strengths and weaknesses.  

📌 **Example Output:**  
- **Overall Score:** XX/100  
- **Strengths:** Strong technical skills, extensive experience, etc.  
- **Weaknesses:** Lack of open-source contributions, weak problem-solving skills, etc.  

---

📌 **Language Detection:**  
First, **detect the language of the CV**. If the CV is in **English**, provide the response in **English**. If it's in **Turkish**, respond in **Turkish**.  

**CV Content:**  
{text}
"""

    try:
        response = Model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API hatası: {e}")
        return None


st.title("Advanced Resume Analysis Application")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    if text: 
        with st.spinner("Analyzing Resume..."):
            analysis_result = analyzecv_pdf_withllm(text)
            if analysis_result: 
                st.subheader("Resume Analysis Results")
                st.write(analysis_result)
