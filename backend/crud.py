from sys import maxsize
import json
import re
import google.generativeai as genai
import fitz
from docx import Document
from async_lru import alru_cache


# ------------- HELPER FUNCTIONS ------------------------
async def get_ai_response(field1,field2,type):
    # Convert inputs to strings to make them hashable for the lru_cache
    field1_str = json.dumps(field1, default=str) if not isinstance(field1, str) else field1
    field2_str = json.dumps(field2, default=str) if not isinstance(field2, str) else field2
    
    data = await ask_ai(field1_str, field2_str, type)
    return data
    
@alru_cache(maxsize = 100)
async def ask_ai(field1: str, field2: str, type: str = 'overview'):
    
    prompt1 = f"""
        # Persona
        You are an elite Labor Market Data Scientist and Career Intelligence Strategist. You specialize in analyzing job market trends, skills gaps, and hiring demands. Your insights are data-driven, actionable, and tailored to help tech professionals and executives make strategic career decisions.

        # Objective
        Analyze the comparative hiring demand and skill requirements between the following job roles to generate a high-value, concise executive summary.

        # Input Data
        1. Role Hiring Volume (Total Job Postings):
        {field1}

        2. Skill Matrix & Percentage Distribution (How often skills appear for these roles):
        {field2}

        # Output Requirements
        Analyze the data and return a SINGLE JSON object with exactly 3 keys:
        - "role_insights": 1 concise sentences analyzing the hiring demand. Identify the dominant role in terms of total postings and highlight the volume gap or trend.
        - "skill_insights": 1 concise sentences analyzing the skill matrix. Identify the foundational skills shared across the roles, and pinpoint the specialized skills that differentiate them.
        - "takeaway": One strategic, forward-looking takeaway. Offer actionable advice for a candidate trying to pivot between these roles or maximize their marketability.

        # Tone and Style
        - Professional, analytical, and authoritative.
        - Avoid fluff; be direct and data-centric.
        - Do not use first-person pronouns ("I", "we").

        Return ONLY a valid, raw JSON object (no markdown, no backticks, no extra text):
        {{"role_insights": "...", "skill_insights": "...", "takeaway": "..."}}
    """

    prompt2 = f"""
        You are a job market analyst. You are given monthly job posting data for a specific year.
        Data (JSON format - month name and number of job postings):
        {field1}
        and most mentioned location and skill and total number of postings :{field2}

        Analyze this data and return a SINGLE JSON object with exactly 3 keys:
        - "brief": 5-7 words. The single most important takeaway (e.g. peak month or trend).
        - "detail": 2 sentences, max 40 words. Cover: peak month with count, lowest month with count, and one trend observation.
        - "overview" : 3-4 line sentence, cover most mentioned location, skill and total postings recorded till no. explai that in brief.
        Return ONLY a raw JSON object (no markdown, no extra text):
        {{"brief": "...", "detail": "...", "overview": "..."}}
        """
    try:
        prompt = ""
        if type == "overview":
            prompt = prompt2
        elif type == "comparision":
            prompt  = prompt1

        model = genai.GenerativeModel('gemini-flash-lite-latest')
        model_response = await model.generate_content_async(prompt)
        raw = model_response.text.strip()

        if not raw:
            return []

        # Strip markdown code blocks if model added them despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        clean_response = json.loads(raw)
        return clean_response
    except Exception as e:
        return []


def extract_pdf(file):
    data = fitz.open(stream=file.read(), filetype='pdf')
    text = ""
    for page in data:
        text += page.get_text()
    return text


def extract_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def analyze_gap(text, required_set):
    matched_skill = set()
    missing_skill = set()
    for skill in required_set:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            matched_skill.add(skill)
        else:
            missing_skill.add(skill)
    return matched_skill, missing_skill
