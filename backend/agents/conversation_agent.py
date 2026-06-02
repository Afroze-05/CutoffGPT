"""
CollegePath AI — Conversation Agent
Manages multi-turn agentic dialogue to gather student preferences.
"""
import json
import re
from loguru import logger
from backend.services.groq_service import get_groq_service


SYSTEM_PROMPT = """You are CollegePath AI, a friendly and intelligent college admission counselor for Maharashtra engineering students.

Your job is to:
1. Greet the student warmly after their marksheet is analyzed
2. Ask ONLY the necessary preference questions — one or two at a time
3. Extract answers from student's natural language replies
4. Confirm collected data naturally
5. Once all preferences are collected, summarize and trigger recommendations

Preferences to collect (ask naturally, not as a form):
- preferred_branches: Which engineering branch interests them? (Computer/IT/AIDS/Mechanical/Civil/E&TC etc.)
- preferred_cities: City preference? (Pune / Mumbai / Nagpur / Aurangabad / Any)
- budget_max_lpa: Annual fee budget in rupees (e.g. 1.5 lakh, 2 lakh, any)
- hostel_required: Do they need hostel? (yes/no/maybe)
- college_type_pref: Government or Private or Any
- priority: What matters more — placements or low fees or both?

Rules:
- Be conversational and empathetic
- Ask 1-2 questions at a time max
- When student gives vague answers, gently clarify
- Use simple English mixed with common terms students use
- NEVER ask all questions at once
- After collecting all preferences, say: "Great! I have everything I need. Let me find the best colleges for you! 🎯"
- Always return a JSON block at the END of your message (hidden from display) with collected data:
  <extracted_data>{"field": "value", ...}</extracted_data>
- Mark preferences_complete: true ONLY when ALL 6 fields are collected

Current step tracking: respond naturally then append the JSON data block."""


class ConversationAgent:
    """Agentic conversation manager for collecting student preferences."""

    def __init__(self):
        self.groq = get_groq_service()

    async def process_message(
        self,
        user_message: str,
        conversation_history: list[dict],
        current_preferences: dict,
        student_info: dict,
    ) -> dict:
        """
        Process a student message and return AI response + updated preferences.
        Returns: {response: str, updated_preferences: dict, preferences_complete: bool}
        """
        # Build context
        context = self._build_context(student_info, current_preferences)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
        ]

        # Add conversation history
        for msg in conversation_history[-10:]:  # last 10 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            response_text = await self.groq.chat(
                messages=messages[1:],  # exclude system from messages list (passed separately)
                system_prompt=SYSTEM_PROMPT + "\n\n" + context,
                temperature=0.5,
                max_tokens=1024,
            )
        except Exception as e:
            logger.error(f"Conversation agent error: {e}")
            response_text = "I'm sorry, I had trouble processing that. Could you please repeat?"

        # Extract data from response
        extracted_data, clean_response = self._extract_data(response_text)

        # Merge with existing preferences
        updated_prefs = {**current_preferences}
        for key, val in extracted_data.items():
            if val is not None and val != "" and key != "preferences_complete":
                updated_prefs[key] = val

        preferences_complete = (
            extracted_data.get("preferences_complete", False) or
            self._check_complete(updated_prefs)
        )

        return {
            "response": clean_response,
            "updated_preferences": updated_prefs,
            "preferences_complete": preferences_complete,
        }

    async def generate_initial_greeting(self, student_info: dict) -> str:
        """Generate personalized greeting after marksheet analysis."""
        name = student_info.get("student_name") or "there"
        exam = student_info.get("exam_type", "CET")
        percentile = student_info.get("percentile")
        percentage = student_info.get("percentage")
        category = student_info.get("category", "OPEN")

        score_text = ""
        if percentile:
            score_text = f"MHT-CET percentile of **{percentile}**"
        elif percentage:
            score_text = f"overall percentage of **{percentage}%**"

        prompt = f"""Generate a warm, encouraging greeting for a student with these details:
- Name: {name}
- Exam: {exam}
- Score: {score_text or 'score not detected clearly'}
- Category: {category}

Then ask about their preferred engineering branch in a friendly way.
Keep it short (3-4 sentences max). Be encouraging about their score."""

        try:
            response = await self.groq.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are CollegePath AI, a friendly college counselor. Be warm, encouraging, and conversational.",
                temperature=0.6,
                max_tokens=300,
            )
            return response
        except Exception as e:
            logger.error(f"Greeting generation error: {e}")
            score_str = f"with a {score_text}" if score_text else ""
            return (
                f"Hello {name}! 👋 Great to meet you! I've analyzed your marksheet "
                f"{score_str}. Now let me help you find the perfect engineering college. "
                f"First — which branch are you most interested in? "
                f"(Computer Engineering, IT, AI & DS, Mechanical, Civil, E&TC, etc.)"
            )

    def _build_context(self, student_info: dict, preferences: dict) -> str:
        """Build context string for the LLM."""
        ctx_parts = ["=== STUDENT CONTEXT ==="]

        if student_info:
            ctx_parts.append(f"Student Name: {student_info.get('student_name', 'Unknown')}")
            ctx_parts.append(f"Exam Type: {student_info.get('exam_type', 'CET')}")
            if student_info.get("percentile"):
                ctx_parts.append(f"Percentile: {student_info['percentile']}")
            if student_info.get("percentage"):
                ctx_parts.append(f"Percentage: {student_info['percentage']}%")
            if student_info.get("rank"):
                ctx_parts.append(f"Rank: {student_info['rank']}")
            ctx_parts.append(f"Category: {student_info.get('category', 'OPEN')}")

        ctx_parts.append("\n=== COLLECTED PREFERENCES ===")
        collected = []
        missing = []
        fields = {
            "preferred_branches": "Branch preference",
            "preferred_cities": "City preference",
            "budget_max_lpa": "Annual fee budget",
            "hostel_required": "Hostel needed",
            "college_type_pref": "College type (Govt/Private)",
            "priority": "Priority (placement/fees/both)",
        }
        for field, label in fields.items():
            val = preferences.get(field)
            if val is not None and val != [] and val != "":
                collected.append(f"✅ {label}: {val}")
            else:
                missing.append(f"❌ {label}: NOT YET COLLECTED")

        ctx_parts.extend(collected)
        ctx_parts.extend(missing)

        if missing:
            ctx_parts.append(f"\nStill need to collect: {len(missing)} preferences")
        else:
            ctx_parts.append("\nAll preferences collected! Ready to generate recommendations.")

        return "\n".join(ctx_parts)

    def _extract_data(self, response: str) -> tuple[dict, str]:
        """Extract JSON data block from response and clean the display text."""
        extracted = {}
        clean = response

        # Look for <extracted_data>...</extracted_data>
        match = re.search(r'<extracted_data>(.*?)</extracted_data>', response, re.DOTALL)
        if match:
            try:
                extracted = json.loads(match.group(1).strip())
            except Exception:
                pass
            clean = response.replace(match.group(0), "").strip()

        return extracted, clean

    def _check_complete(self, prefs: dict) -> bool:
        """Check if all necessary preferences are collected."""
        required = ["preferred_branches", "preferred_cities", "budget_max_lpa",
                    "hostel_required", "college_type_pref", "priority"]
        for field in required:
            val = prefs.get(field)
            if val is None or val == [] or val == "":
                return False
        return True
