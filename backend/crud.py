from sys import maxsize
import asyncio
import json
from datetime import datetime
import re
import google.generativeai as genai
import fitz
from docx import Document
from async_lru import alru_cache


# ------------- ASK AI SETTINGS ------------------------

CHAT_MODEL = "gemini-3.5-flash-lite"

CHAT_PROMPT = """
    # Persona
    You are InternIQ's market assistant. You help students and job seekers understand
    the internship and entry-level job market in India.

    # Your data
    At the end of these instructions you are given one JSON object with the data
    shown on the InternIQ dashboard:
    - "pipeline": when the job data was last scraped.
    - "market_overview": yearly totals, top roles, most demanded skill, top location,
      monthly job postings and top hiring companies.
    - "comparative_analysis": total postings, skill share (percentage of postings that
      mention each skill) and monthly postings for the roles a user compared.
    - "recent_market_trends": totals, top role, top skill, top locations, average stipend
      and individual job postings from the last 10 days.
    Inside each section, the keys such as "field=all" or "year=2026, field=backend"
    describe which filter the numbers belong to.

    # How to answer
    - Answer ONLY from the dashboard data. Never invent numbers, companies, roles or trends.
    - If the data does not contain the answer, say so plainly and mention what you
      can answer instead (roles, skills, locations, companies, postings, stipends).
    - Quote exact numbers from the data and say which period they cover
      (this year, a given month, or the last 10 days).
    - A negative percent change is a decrease and a positive one is an increase;
      always say which it is (for example "down 68.8%").
    - The data stores every name in lowercase. In your answer, always start each word of
      a skill, role, company or location name with a capital letter, for example
      write "Python", "Data Engineer", "Tata Consultancy Services" and "Work From Home",
      never "python" or "data engineer". Keep short codes in capitals, such as "AI" and "SQL".
    - Keep answers short: 2 to 4 sentences, or a short list when comparing items.
    - Reply in plain text. Do not use markdown, tables or emojis.
"""


# ------------- HELPER FUNCTIONS ------------------------
async def get_ai_response(field1,field2,type):
    # Ask AI questions: field1 is the user's question, field2 is the dashboard data.
    # They skip the lru_cache below so a failed answer is never cached and repeated.
    if type == 'chat':
        data = await answer_chat_question(field1, field2)
        return data

    # Convert inputs to strings to make them hashable for the lru_cache
    field1_str = json.dumps(field1, default=str) if not isinstance(field1, str) else field1
    field2_str = json.dumps(field2, default=str) if not isinstance(field2, str) else field2

    data = await ask_ai(field1_str, field2_str, type)
    return data


async def answer_chat_question(question, dashboard_data):
    """
    Answers a user's question from the dashboard data.
    The data is added to the system instruction, so Gemini reads it as fixed
    background knowledge and the user's question is sent as the message.
    """
    data_json = json.dumps(dashboard_data, default=str)
    system_instruction = f"""
        {CHAT_PROMPT}

        # Dashboard data
        {data_json}
    """

    try:
        model = genai.GenerativeModel(CHAT_MODEL, system_instruction=system_instruction)

        # generate_content_async does not work with transport="rest" (set in main.py),
        # so call the normal version in a background thread instead.
        model_response = await asyncio.to_thread(
            model.generate_content,
            question,
            request_options={"timeout": 60},
        )
        return {"answer": model_response.text.strip()}

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return {"error": "API quota exceeded. Ask AI is unavailable temporarily."}
        return {"error": f"AI service error: {error_msg[:100]}"}

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
                    NOTE: Today's date is {datetime.now().strftime("%B %d, %Y")}. If we are currently at the very beginning of the month, 
                    the current month's job count will naturally be much lower. Do NOT falsely report this as a "massive drop" or decline; instead,
                    explicitly state that the current month has just started so data is still accumulating.
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
        model_response = await model.generate_content_async(
            prompt,
            request_options={"timeout": 60},
        )
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
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return {"error": "API quota exceeded. Insights unavailable temporarily."}
        return {"error": f"AI service error: {error_msg[:100]}"}


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
    '''
    Searches in the whole document text for the skills , and finds is it there
    or not.if yes, then add it to the matched set
    '''

    matched_skill = set()
    missing_skill = set()
    for skill in required_set:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            matched_skill.add(skill)
        else:
            missing_skill.add(skill)
    return matched_skill, missing_skill
