"""
CollegePath AI — Recommendation Agent (Agentic Core)
Uses Groq LLM + cutoff DB to generate dream/target/safe college lists.
"""
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from loguru import logger
from backend.services.groq_service import get_groq_service
from backend.models.college import College, CutoffRecord


class RecommendationAgent:
    """
    Agentic AI that:
    1. Queries the cutoff DB based on student profile
    2. Scores and ranks colleges
    3. Classifies them as Dream / Target / Safe
    4. Uses Groq to generate personalized reasoning
    """

    def __init__(self):
        self.groq = get_groq_service()

    async def generate_recommendations(
        self,
        db: AsyncSession,
        student_profile: dict,
    ) -> dict:
        """
        Main agentic recommendation pipeline.
        Returns {dream: [...], target: [...], safe: [...]}
        """
        logger.info(f"Generating recommendations for: {student_profile}")

        # Step 1: Fetch relevant cutoff records
        cutoffs = await self._fetch_cutoffs(db, student_profile)
        logger.info(f"Found {len(cutoffs)} cutoff records")

        # Step 2: Fetch college details
        college_data = await self._fetch_colleges(db)

        # Step 3: Score and classify colleges
        scored = self._score_colleges(cutoffs, college_data, student_profile)

        # Step 4: Use Groq to generate reasoning and final list
        recommendations = await self._ai_classify(scored, student_profile)

        return recommendations

    async def _fetch_cutoffs(self, db: AsyncSession, profile: dict) -> list[dict]:
        """Fetch matching cutoff records from DB."""
        category = profile.get("category", "OPEN")
        preferred_branches = profile.get("preferred_branches", [])
        exam_type = profile.get("exam_type", "CET")

        conditions = [
            CutoffRecord.exam_type == exam_type,
            CutoffRecord.year >= 2022,
            or_(
                CutoffRecord.category == category,
                CutoffRecord.category == "OPEN",
            ),
        ]

        if preferred_branches:
            branch_conditions = []
            for branch in preferred_branches:
                branch_conditions.append(CutoffRecord.branch_name.ilike(f"%{branch}%"))
            if branch_conditions:
                from sqlalchemy import or_ as sq_or
                conditions.append(sq_or(*branch_conditions))

        result = await db.execute(
            select(CutoffRecord).where(and_(*conditions)).limit(200)
        )
        records = result.scalars().all()

        return [
            {
                "college_name": r.college_name,
                "branch_name": r.branch_name,
                "exam_type": r.exam_type,
                "year": r.year,
                "round_no": r.round_no,
                "category": r.category,
                "cutoff_percentile": r.cutoff_percentile,
                "cutoff_rank": r.cutoff_rank,
                "college_id": r.college_id,
            }
            for r in records
        ]

    async def _fetch_colleges(self, db: AsyncSession) -> dict:
        """Fetch all college details as lookup dict."""
        result = await db.execute(select(College))
        colleges = result.scalars().all()
        return {
            c.short_name: {
                "id": c.id,
                "name": c.name,
                "short_name": c.short_name,
                "city": c.city,
                "college_type": c.college_type,
                "annual_fees": c.annual_fees,
                "avg_placement_lpa": c.avg_placement_lpa,
                "hostel_available": c.hostel_available,
                "naac_grade": c.naac_grade,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "top_recruiters": c.top_recruiters,
                "facilities": c.facilities,
                "about": c.about,
            }
            for c in colleges
        }

    def _score_colleges(
        self,
        cutoffs: list[dict],
        college_data: dict,
        profile: dict,
    ) -> list[dict]:
        """
        Score each college-branch combo based on:
        - Cutoff delta (how far is student from cutoff)
        - Preference matches (city, fees, hostel)
        """
        student_percentile = profile.get("percentile") or 85.0
        preferred_cities = [c.lower() for c in (profile.get("preferred_cities") or [])]
        budget = profile.get("budget_max_lpa") or 200000
        hostel_needed = (profile.get("hostel_required") or "no").lower() in ("yes", "maybe")
        priority = profile.get("priority", "both")

        scored = {}

        for record in cutoffs:
            key = f"{record['college_name']}||{record['branch_name']}"
            cutoff_p = record.get("cutoff_percentile")
            if cutoff_p is None:
                continue

            delta = student_percentile - cutoff_p  # positive = student above cutoff

            # Base admission probability
            if delta >= 5:
                probability = 0.95
                tier = "safe"
            elif delta >= 1:
                probability = 0.75
                tier = "target"
            elif delta >= -3:
                probability = 0.45
                tier = "target"
            elif delta >= -7:
                probability = 0.2
                tier = "dream"
            else:
                probability = 0.05
                tier = "dream"

            # Bonus scoring
            bonus = 0.0

            # Find matching college details
            col_info = None
            for short_name, info in college_data.items():
                if (short_name.lower() in record["college_name"].lower() or
                        record["college_name"].lower() in info["name"].lower()):
                    col_info = info
                    break

            if col_info:
                # City match
                if preferred_cities and col_info.get("city", "").lower() in preferred_cities:
                    bonus += 0.1
                # Budget match
                if col_info.get("annual_fees") and col_info["annual_fees"] <= budget:
                    bonus += 0.05
                # Hostel
                if hostel_needed and col_info.get("hostel_available"):
                    bonus += 0.05
                # Placement priority
                if priority == "placement" and col_info.get("avg_placement_lpa", 0) > 7:
                    bonus += 0.08
                # Government preference
                if profile.get("college_type_pref") == "Government" and col_info.get("college_type") == "Government":
                    bonus += 0.1

            final_prob = min(0.99, probability + bonus)

            if key not in scored or scored[key]["probability"] < final_prob:
                scored[key] = {
                    "college_name": record["college_name"],
                    "branch_name": record["branch_name"],
                    "cutoff_percentile": cutoff_p,
                    "student_percentile": student_percentile,
                    "delta": round(delta, 2),
                    "probability": round(final_prob, 2),
                    "tier": tier,
                    "college_info": col_info or {},
                }

        return list(scored.values())

    async def _ai_classify(self, scored: list[dict], profile: dict) -> dict:
        """Use Groq AI to intelligently classify and reason about recommendations."""

        # Limit to top 30 to avoid token limits
        top_colleges = sorted(scored, key=lambda x: x["probability"], reverse=True)[:30]

        if not top_colleges:
            return {"dream": [], "target": [], "safe": [], "summary": "No matching colleges found for your profile."}

        system = """You are CollegePath AI, an expert Maharashtra engineering college admission counselor.
Analyze the student profile and college matches, then:
1. Classify colleges into Dream (< 30% chance), Target (30-80%), Safe (> 80%)
2. Select the BEST 3-4 per category
3. Add personalized reasoning for each recommendation
4. Write a brief summary paragraph

Return ONLY a valid JSON object with this structure:
{
  "dream": [
    {
      "college_name": "...",
      "branch_name": "...",
      "probability_percent": 25,
      "cutoff_percentile": 99.1,
      "annual_fees": 85000,
      "avg_placement_lpa": 11.0,
      "city": "Pune",
      "college_type": "Government",
      "hostel_available": true,
      "reason": "Personalized 1-2 sentence reason",
      "pros": ["...", "..."],
      "cons": ["..."]
    }
  ],
  "target": [...],
  "safe": [...],
  "summary": "Overall 2-3 sentence personalized summary for the student"
}"""

        prompt = f"""Student Profile:
- Percentile: {profile.get('percentile')}
- Category: {profile.get('category', 'OPEN')}
- Preferred Branches: {profile.get('preferred_branches', [])}
- Preferred Cities: {profile.get('preferred_cities', [])}
- Budget: ₹{profile.get('budget_max_lpa', 200000):,}/year
- Hostel Needed: {profile.get('hostel_required', 'no')}
- College Type Preference: {profile.get('college_type_pref', 'Any')}
- Priority: {profile.get('priority', 'both')}

College Matches (scored):
{json.dumps(top_colleges[:25], indent=2)}

Classify these into Dream/Target/Safe and provide recommendations."""

        try:
            resp = await self.groq.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system,
                temperature=0.2,
                max_tokens=3000,
            )
            # Extract JSON
            import re
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            if match:
                result = json.loads(match.group())
                return result
        except Exception as e:
            logger.error(f"AI classification error: {e}")

        # Fallback: simple classification
        dream = [c for c in top_colleges if c["tier"] == "dream"][:3]
        target = [c for c in top_colleges if c["tier"] == "target"][:4]
        safe = [c for c in top_colleges if c["tier"] == "safe"][:3]

        return {
            "dream": dream,
            "target": target,
            "safe": safe,
            "summary": f"Based on your percentile of {profile.get('percentile')}, here are your college options."
        }
