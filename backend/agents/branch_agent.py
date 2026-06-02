"""
CollegePath AI — Branch Guidance Agent
Interest-based branch recommendation using Groq.
"""
import json
import re
from loguru import logger
from backend.services.groq_service import get_groq_service


BRANCH_QUESTIONS = [
    {"id": "coding", "question": "Do you enjoy coding or programming?", "options": ["Yes, love it!", "A little", "Not really", "Never tried"]},
    {"id": "electronics", "question": "Are you interested in electronics and circuits?", "options": ["Yes, very much", "Somewhat", "Not really", "Prefer software"]},
    {"id": "ai_interest", "question": "Are you excited about AI, Machine Learning, and Data?", "options": ["Absolutely!", "Somewhat", "Not sure", "Prefer other fields"]},
    {"id": "design", "question": "Do you like designing things — machines, buildings, or products?", "options": ["Yes, love design", "Sometimes", "Not really", "Prefer analysis"]},
    {"id": "math", "question": "How comfortable are you with advanced mathematics?", "options": ["Very comfortable", "Average", "Somewhat weak", "Prefer practical work"]},
    {"id": "hardware_software", "question": "Do you prefer working with hardware or software?", "options": ["Hardware (physical things)", "Software (digital/programs)", "Both equally", "Neither sure"]},
    {"id": "career_goal", "question": "What's your career vision?", "options": ["IT/Software company", "Core engineering (manufacturing/auto)", "Research/Academia", "Startup/Entrepreneurship", "Government/PSU"]},
]


class BranchGuidanceAgent:
    """AI agent that recommends engineering branches based on student interests."""

    def __init__(self):
        self.groq = get_groq_service()

    def get_questions(self) -> list[dict]:
        return BRANCH_QUESTIONS

    async def recommend_branches(self, answers: dict) -> dict:
        """
        Given interest answers, recommend top engineering branches.
        Returns structured recommendations with reasoning.
        """
        system = """You are an expert engineering career counselor specializing in Maharashtra engineering admissions.
Based on student interest answers, recommend the best engineering branches.
Return ONLY a valid JSON object with this structure:
{
  "top_branch": "Computer Engineering",
  "recommendations": [
    {
      "branch": "Computer Engineering",
      "short": "COMP",
      "match_percent": 95,
      "why": "2-3 sentence personalized reason based on their answers",
      "career_paths": ["Software Engineer", "AI Engineer", "Product Manager"],
      "scope": "Excellent — highest demand, best salaries in current market",
      "avg_salary_range": "₹5-25 LPA"
    },
    ...
  ],
  "avoid_branches": ["Civil Engineering"],
  "avoid_reason": "Based on your low interest in design and preference for software...",
  "overall_advice": "Personalized 2-3 sentence overall advice"
}
Include 3-4 recommended branches total."""

        prompt = f"""Student interest profile (from quiz answers):
{json.dumps(answers, indent=2)}

Available branches in Maharashtra engineering:
- Computer Engineering (COMP)
- Information Technology (IT)
- AI & Data Science (AIDS)
- Electronics & Telecommunication (E&TC)
- Mechanical Engineering (MECH)
- Civil Engineering (CIVIL)
- Electrical Engineering (ELEC)
- Computer Science & Engineering (CSE)

Recommend the best branches for this student."""

        try:
            resp = await self.groq.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system,
                temperature=0.3,
                max_tokens=2000,
            )
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"Branch guidance error: {e}")

        # Fallback
        return {
            "top_branch": "Computer Engineering",
            "recommendations": [
                {
                    "branch": "Computer Engineering",
                    "short": "COMP",
                    "match_percent": 80,
                    "why": "Computer Engineering is the most versatile branch with excellent job opportunities.",
                    "career_paths": ["Software Engineer", "Developer", "Data Analyst"],
                    "scope": "Excellent",
                    "avg_salary_range": "₹5-20 LPA"
                }
            ],
            "avoid_branches": [],
            "avoid_reason": "",
            "overall_advice": "Choose a branch that aligns with your interests and career goals."
        }

    async def chat_about_branches(
        self,
        user_message: str,
        history: list[dict],
    ) -> str:
        """Open-ended chat about branch selection."""
        system = """You are CollegePath AI's branch counselor.
Help students understand different engineering branches in Maharashtra.
Give practical, honest advice about job scope, salary, college culture, and what each branch involves.
Keep responses conversational, under 200 words, use emojis sparingly."""

        messages = history[-6:] + [{"role": "user", "content": user_message}]

        try:
            return await self.groq.chat(
                messages=messages,
                system_prompt=system,
                temperature=0.5,
                max_tokens=400,
            )
        except Exception as e:
            logger.error(f"Branch chat error: {e}")
            return "I had trouble responding. Please try again!"
