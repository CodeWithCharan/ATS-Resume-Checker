import streamlit as st
import google.generativeai as genai
import os
import json
import PyPDF2 as pdf
from dotenv import load_dotenv

load_dotenv() # load all our environment variables

# config API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# response function
def get_response(input_prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(input_prompt)
        return response.text
    except Exception as e:
        st.error(f"API call failed: {str(e)}")
        return None
    
# get text from pdf
def get_pdf_text(uploaded_resume):
    try:
        reader = pdf.PdfReader(uploaded_resume)
        text = ""

        # loop through every single page
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text
    
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {str(e)}")
        return None

# prompt template function
def get_prompt_template(text, jd):
    return f"""
    Hey Act Like a skilled ATS (Application Tracking System) with a deep understanding of the tech field 
    (Data Science, Machine Learning, Data Analyst, and Big Data Engineer). 
    Your task is to evaluate the resume based on the given job description. 
    The job market is very competitive, so provide the best assistance for improving their resumes.
    Assign the percentage matching based on the job description and list the missing keywords with high accuracy.
    resume: {text}
    description: {jd}

    I want the response in one single string having the structure
    {{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
    """

# streamlit app
st.set_page_config(page_title="Resume Checker", page_icon="📝")
st.title("ATS Resume Checker")
st.text("""
    This is an AI-powered resume checker that helps you optimize your resume for
    any job description, highlighting the percentage match based on the job description
    and the skills recruiters are looking for.
""")

jd = st.text_area("Paste the Job Description")
uploaded_resume = st.file_uploader("Upload Your Resume (PDF only)",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_resume is not None and jd:
        with st.spinner("Analyzing your resume..."):
            text = get_pdf_text(uploaded_resume)
            input_prompt = get_prompt_template(text, jd)
            response = get_response(input_prompt)
            if response:
                    try:
                        # Parse and display the structured response
                        result = json.loads(response)
                        st.subheader("Response:")
                        st.write(f"**Job Description Match**: {result['JD Match']}")
                        st.write(f"**Missing Keywords**: {', '.join(result['MissingKeywords'])}")
                        st.write(f"**Profile Summary**: {result['Profile Summary']}")
                    except json.JSONDecodeError:
                        st.error("Failed to parse the response from the API.")