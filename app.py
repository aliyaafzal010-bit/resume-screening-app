import streamlit as st
import pdfplumber
import docx2txt
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# Extract Text
# -------------------------------
def extract_text(file):
    text = ""
    
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                
    elif file.name.endswith(".docx"):
        text = docx2txt.process(file)
    
    return text


# -------------------------------
# Extract Email & Phone
# -------------------------------
def extract_email(text):
    return re.findall(r'\S+@\S+', text)

def extract_phone(text):
    return re.findall(r'\b\d{10}\b', text)


# -------------------------------
# Skills
# -------------------------------
skills_db = [
    "python","java","sql","machine learning","ai",
    "data science","deep learning","html","css","javascript"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_db if skill in text]


# -------------------------------
# Similarity
# -------------------------------
def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]


# -------------------------------
# UI
# -------------------------------
st.title("📄 AI Resume Screening System")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
job_description = st.text_area("Enter Job Description")

if st.button("Analyze Resume"):
    
    if uploaded_file and job_description:
        
        text = extract_text(uploaded_file)
        
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        
        similarity = calculate_similarity(text, job_description)
        
        jd_skills = extract_skills(job_description)
        skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)
        
        final_score = (0.7 * similarity) + (0.3 * skill_score)
        
        st.write("Email:", email)
        st.write("Phone:", phone)
        st.write("Skills:", skills)
        
        st.write("Similarity:", round(similarity,2))
        st.write("Final Score:", round(final_score,2))
