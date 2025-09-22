import os
import json
import re
import logging
import random
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", getattr(settings, "OPENAI_API_KEY", None))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo"))
TTL = int(os.getenv("OPENAI_SUGGESTION_TTL", getattr(settings, "OPENAI_SUGGESTION_TTL", 3600)))

# lazy import openai
openai = None
if OPENAI_API_KEY:
    try:
        import openai as _openai
        _openai.api_key = OPENAI_API_KEY
        openai = _openai
    except Exception as e:
        logger.exception("Failed to import openai: %s", e)
        openai = None

# Random task templates
RANDOM_TASKS = [
    {"title": "Review class notes from last week", "time_minutes": 10, "reason": "Reinforce learning"},
    {"title": "Solve 5 quick math problems", "time_minutes": 15, "reason": "Practice makes perfect"},
    {"title": "Read a short educational article", "time_minutes": 12, "reason": "Expand knowledge"},
    {"title": "Organize your study materials", "time_minutes": 8, "reason": "Stay organized"},
    {"title": "Practice vocabulary words", "time_minutes": 10, "reason": "Build language skills"},
    {"title": "Review homework assignments", "time_minutes": 15, "reason": "Stay on track"},
    {"title": "Create flashcards for upcoming test", "time_minutes": 18, "reason": "Prepare for exams"},
    {"title": "Summarize today's lesson", "time_minutes": 12, "reason": "Reinforce understanding"},
    {"title": "Practice handwriting or typing", "time_minutes": 10, "reason": "Improve skills"},
    {"title": "Plan your study schedule", "time_minutes": 8, "reason": "Time management"},
    {"title": "Review previous test questions", "time_minutes": 15, "reason": "Learn from mistakes"},
    {"title": "Practice pronunciation (if language subject)", "time_minutes": 10, "reason": "Improve speaking"},
    {"title": "Draw a mind map of a topic", "time_minutes": 12, "reason": "Visual learning"},
    {"title": "Write a short reflection", "time_minutes": 10, "reason": "Critical thinking"},
    {"title": "Practice problem-solving techniques", "time_minutes": 15, "reason": "Develop skills"},
    {"title": "Review textbook chapter summary", "time_minutes": 10, "reason": "Key concepts"},
    {"title": "Practice speed reading", "time_minutes": 8, "reason": "Improve reading skills"},
    {"title": "Create a study playlist", "time_minutes": 5, "reason": "Motivation boost"},
    {"title": "Review class syllabus", "time_minutes": 8, "reason": "Stay informed"},
    {"title": "Practice mental math", "time_minutes": 10, "reason": "Quick calculations"}
]

def _build_prompt(student):
    pref = getattr(student, "preferences", "") or ""
    grade = getattr(student, "grade", "") or ""
    subjects = getattr(student, "subjects", None)
    subj_str = ", ".join([s.name for s in subjects.all()]) if subjects else ""
    return (
        f"Student preferences: {pref}. Subjects: {subj_str}. Grade: {grade}. "
        "Suggest 3 short actionable tasks for a free period (5-20 minutes each). "
        "Return a JSON array of objects with 'title', 'time_minutes', and 'reason'. Keep concise."
    )

def parse_suggestions_from_text(text):
    if not text:
        return []
    m = re.search(r"(\[.*\])", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            logger.exception("Failed to parse JSON from OpenAI response")
    # fallback: break into lines
    lines = [ln.strip("- ") for ln in text.splitlines() if ln.strip()]
    return [{"title": lines[i][:200], "time_minutes": 10, "reason": "parsed fallback"} for i in range(min(len(lines), 3))]

def generate_random_tasks(count=3):
    """Generate random tasks from the predefined list"""
    return random.sample(RANDOM_TASKS, min(count, len(RANDOM_TASKS)))

def get_suggestions_for_student(student, force_refresh=False):
    if student is None:
        return []

    cache_key = f"ai_sugg:student:{student.id}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    prompt = _build_prompt(student)
    text = None

    if openai:
        try:
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a concise assistant that replies with a JSON array."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.2,
            )
            try:
                text = resp.choices[0].message["content"]
            except Exception:
                text = getattr(resp.choices[0], "text", str(resp))
        except Exception as e:
            logger.exception("OpenAI call failed: %s", e)
            text = None

    if not text:
        # fallback defaults
        suggestions = [
            {"title": "Review last class notes", "time_minutes": 10, "reason": "Fallback"},
            {"title": "Solve 3 quick practice problems", "time_minutes": 15, "reason": "Fallback"},
            {"title": "Read a short article", "time_minutes": 15, "reason": "Fallback"},
        ]
        cache.set(cache_key, suggestions, TTL)
        return suggestions

    suggestions = parse_suggestions_from_text(text)
    cache.set(cache_key, suggestions, TTL)
    return suggestions
