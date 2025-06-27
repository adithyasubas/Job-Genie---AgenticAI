import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
from fpdf import FPDF
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with error handling
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        st.error(" OpenAI API key not found. Please create a .env file with OPENAI_API_KEY=your_key")
        st.stop()
except Exception as e:
    st.error(f" Failed to initialize OpenAI client: {str(e)}")
    st.stop()

# ===== Function Definitions =====

def extract_keywords(resume, job_title):
    prompt = f"""
    You are a helpful assistant. Based on the following resume and the target job title: '{job_title}',
    generate a list of 5 to 10 relevant job search keywords.

    Resume:
    {resume}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content

def generate_mock_job_listings(keywords):
    prompt = f"""
    Create 3 fictional job listings suitable for someone with the following skills/keywords:
    {keywords}

    Each job listing should include:
    - Job Title
    - Company Name
    - Location
    - Job Description (4-5 lines)
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content

def generate_cover_letter(resume, job_listing):
    prompt = f"""
    Write a professional cover letter for this job listing using the candidate's resume.
    The cover letter should:
    - Be 3-4 paragraphs
    - Highlight relevant skills from the resume
    - Match the tone of the job listing
    - Not include any fictional details

    Job Listing:
    {job_listing}

    Resume:
    {resume}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content

def generate_interview_prep(resume, job_listing):
    prompt = f"""
    Based on this job listing and resume, generate:
    1. 5 likely interview questions
    2. Suggested answers using the resume content

    Format as:
    ### Questions:
    1. Question 1
    2. Question 2
    ...
    
    ### Suggested Answers:
    1. Answer 1 (using resume details)
    2. Answer 2 (using resume details)
    ...

    Job Listing:
    {job_listing}

    Resume:
    {resume}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content

def generate_pdf(job_packages):
    """Generate PDF using fpdf2 instead of WeasyPrint"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for i, package in enumerate(job_packages, 1):
        pdf.cell(200, 10, txt=f"Job Opportunity #{i}", ln=True, align='C')
        pdf.multi_cell(0, 10, txt=f"Job Listing:\n{package['listing']}")
        pdf.multi_cell(0, 10, txt=f"Cover Letter:\n{package['cover_letter']}")
        pdf.multi_cell(0, 10, txt=f"Interview Preparation:\n{package['interview_prep']}")
        if i < len(job_packages):
            pdf.add_page()
    
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(pdf_file.name)
    return pdf_file.name


# ===== Streamlit App UI =====

st.title(" Job Genie - Your AI Job Coach")

uploaded_file = st.file_uploader(" Upload your Resume (PDF)", type="pdf")
job_title = st.text_input(" What job are you looking for?", placeholder="e.g., Cloud Engineer in Sydney")

resume_text = ""

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        resume_text += page.get_text()
    st.success(" Resume uploaded successfully!")
    st.subheader(" Extracted Resume Preview:")
    st.text_area("Resume Text", resume_text, height=300)

if uploaded_file and job_title:
    st.success(" Ready to search and generate cover letters!")
    
    if st.button(" Generate Full Job Package"):
        with st.spinner("Working on your job application package..."):
            # Step 1: Get keywords
            keywords = extract_keywords(resume_text, job_title)
            
            # Step 2: Generate job listings
            listings = generate_mock_job_listings(keywords)
            
            # Step 3: Generate cover letters and interview prep for each listing
            job_packages = []
            for listing in listings.split('\n\n'):  # Assuming each listing is separated by double newlines
                if listing.strip():
                    cover_letter = generate_cover_letter(resume_text, listing)
                    interview_prep = generate_interview_prep(resume_text, listing)
                    job_packages.append({
                        'listing': listing,
                        'cover_letter': cover_letter,
                        'interview_prep': interview_prep
                    })
            
            # Display results
            st.subheader(" Your Job Application Package")
            
            for i, package in enumerate(job_packages, 1):
                with st.expander(f"Job Opportunity #{i}"):
                    st.markdown(f"**Job Listing:**\n{package['listing']}")
                    st.markdown(f"**Cover Letter:**\n{package['cover_letter']}")
                    st.markdown(f"**Interview Preparation:**\n{package['interview_prep']}")
            
            # Generate PDF button
            if st.button(" Export as PDF"):
                pdf_path = generate_pdf(job_packages)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=" Download PDF",
                        data=f,
                        file_name="job_application_package.pdf",
                        mime="application/pdf"
                    )
                os.unlink(pdf_path)
