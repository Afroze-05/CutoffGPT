"""
CollegePath AI — College Comparison Agent
Generates side-by-side college comparison with AI insights.
"""
import json
import re
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.services.groq_service import get_groq_service
from backend.models.college import College, CutoffRecord


class ComparisonAgent:
    """Compares multiple colleges and generates AI insights."""

    def __init__(self):
        self.groq = get_groq_service()

    async def compare_colleges(
        self,
        db: AsyncSession,
        college_names: list[str],
        student_profile: dict,
    ) -> dict:
        """Compare colleges and return structured comparison + AI verdict."""

        # Fetch college data
        colleges_data = []
        for name in college_names:
            result = await db.execute(
                select(College).where(
                    College.name.ilike(f"%{name}%") |
                    College.short_name.ilike(f"%{name}%")
                )
            )
            college = result.scalar_one_or_none()
            if college:
                # Get latest cutoffs for this college
                cutoff_result = await db.execute(
                    select(CutoffRecord).where(
                        CutoffRecord.college_name.ilike(f"%{college.short_name}%"),
                        CutoffRecord.year >= 2022,
                        CutoffRecord.category == student_profile.get("category", "OPEN"),
                    ).limit(5)
                )
                cutoffs = cutoff_result.scalars().all()
                min_cutoff = min((c.cutoff_percentile for c in cutoffs if c.cutoff_percentile), default=None)

                colleges_data.append({
                    "name": college.name,
                    "short_name": college.short_name,
                    "city": college.city,
                    "college_type": college.college_type,
                    "autonomous": college.autonomous,
                    "naac_grade": college.naac_grade,
                    "annual_fees": college.annual_fees,
                    "avg_placement_lpa": college.avg_placement_lpa,
                    "hostel_available": college.hostel_available,
                    "top_recruiters": college.top_recruiters or [],
                    "facilities": college.facilities or [],
                    "about": college.about,
                    "latitude": college.latitude,
                    "longitude": college.longitude,
                    "min_cutoff_percentile": min_cutoff,
                })

        if not colleges_data:
            return {"error": "No matching colleges found", "colleges": []}

        # Generate AI comparison
        ai_verdict = await self._generate_verdict(colleges_data, student_profile)

        return {
            "colleges": colleges_data,
            "comparison_table": self._build_table(colleges_data),
            "ai_verdict": ai_verdict,
        }

    def _build_table(self, colleges: list[dict]) -> list[dict]:
        """Build comparison table rows."""
        rows = [
            {"feature": "City", "values": [c.get("city", "N/A") for c in colleges]},
            {"feature": "Type", "values": [c.get("college_type", "N/A") for c in colleges]},
            {"feature": "NAAC Grade", "values": [c.get("naac_grade", "N/A") for c in colleges]},
            {"feature": "Annual Fees", "values": [f"₹{c['annual_fees']:,.0f}" if c.get("annual_fees") else "N/A" for c in colleges]},
            {"feature": "Avg Placement", "values": [f"₹{c['avg_placement_lpa']} LPA" if c.get("avg_placement_lpa") else "N/A" for c in colleges]},
            {"feature": "Hostel", "values": ["✅ Yes" if c.get("hostel_available") else "❌ No" for c in colleges]},
            {"feature": "Autonomous", "values": ["✅ Yes" if c.get("autonomous") else "No" for c in colleges]},
            {"feature": "Min Cutoff (OPEN)", "values": [f"{c['min_cutoff_percentile']}%" if c.get("min_cutoff_percentile") else "N/A" for c in colleges]},
        ]
        return rows

    async def _generate_verdict(self, colleges: list[dict], profile: dict) -> dict:
        """Use Groq to generate personalized comparison verdict."""
        system = """You are CollegePath AI, an expert Maharashtra engineering admission counselor.
Compare these colleges for a specific student and give a clear verdict.
Return ONLY valid JSON with:
{
  "best_overall": "college short name",
  "best_for_placement": "college short name",
  "best_for_budget": "college short name",
  "best_for_student": "college short name",
  "verdict_reason": "2-3 sentence personalized verdict",
  "college_insights": {
    "ShortName1": {"strength": "...", "weakness": "..."},
    "ShortName2": {"strength": "...", "weakness": "..."}
  }
}"""

        prompt = f"""Student Profile:
- Percentile: {profile.get('percentile')}
- Category: {profile.get('category', 'OPEN')}
- Priority: {profile.get('priority', 'both')}
- Budget: ₹{profile.get('budget_max_lpa', 200000):,}

Colleges to compare:
{json.dumps(colleges, indent=2, default=str)}"""

        try:
            resp = await self.groq.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system,
                temperature=0.3,
                max_tokens=1000,
            )
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"Comparison verdict error: {e}")

        return {
            "best_overall": colleges[0]["short_name"] if colleges else "",
            "verdict_reason": "Based on the data, compare fees, placements and location to make your decision.",
            "college_insights": {}
        }
