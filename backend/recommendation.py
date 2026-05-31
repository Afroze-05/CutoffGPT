"""
recommendation.py - College Recommendation Engine
===================================================
Takes student profile + college database and generates:
  - Dream Colleges  (admission < 40% likely - reach schools)
  - Target Colleges (admission 40-75% likely - realistic picks)
  - Safe Colleges   (admission > 75% likely - guaranteed)

Logic:
  1. Filter colleges by branch preference
  2. Score each college based on cutoff gap, fees, city, etc.
  3. Classify into Dream / Target / Safe
  4. Sort by best match within each category
"""

from typing import List, Dict
import math


def generate_recommendations(student: Dict, colleges: List[Dict]) -> Dict:
    """
    Main function: returns Dream/Target/Safe college lists.
    
    student = {
        percentage, rank, category, preferred_branch,
        preferred_city, budget, hostel_needed, govt_preferred,
        placement_priority
    }
    colleges = list of all college records from DB
    """
    dream, target, safe = [], [], []

    for college in colleges:
        # ── Step 1: Filter by branch ───────────────────────────────
        # Only consider colleges offering student's preferred branch
        if not branch_matches(student["preferred_branch"], college["branch"]):
            continue

        # ── Step 2: Check category-specific cutoff ─────────────────
        # We use percentile comparison (rank can vary year to year)
        student_pct = student.get("percentage", 0)
        college_cutoff = college.get("cutoff_percentile", 0)

        # ── Step 3: Calculate admission probability ────────────────
        probability = calculate_probability(student_pct, college_cutoff, student["category"])

        # ── Step 4: Apply preference scoring ──────────────────────
        preference_score = calculate_preference_score(student, college)

        # ── Step 5: Build recommendation card ─────────────────────
        card = build_recommendation_card(college, probability, preference_score, student)

        # ── Step 6: Classify into Dream / Target / Safe ────────────
        if probability >= 75:
            safe.append(card)
        elif probability >= 40:
            target.append(card)
        else:
            dream.append(card)

    # Sort each list: best preference score first
    dream.sort(key=lambda x: x["preference_score"], reverse=True)
    target.sort(key=lambda x: x["preference_score"], reverse=True)
    safe.sort(key=lambda x: x["preference_score"], reverse=True)

    # Return top picks from each category
    return {
        "dream_colleges": dream[:5],
        "target_colleges": target[:5],
        "safe_colleges": safe[:5],
        "student_summary": {
            "name": student.get("student_name", "Student"),
            "percentage": student["percentage"],
            "category": student["category"],
            "branch": student["preferred_branch"]
        }
    }


def branch_matches(preferred: str, college_branch: str) -> bool:
    """
    Check if college branch matches student preference.
    Uses fuzzy keyword matching for flexibility.
    """
    preferred_lower = preferred.lower()
    college_lower = college_branch.lower()

    # Map common abbreviations
    branch_aliases = {
        "cs": ["computer", "cs"],
        "computer": ["computer", "cs"],
        "ai": ["artificial intelligence", "ai & data", "ai"],
        "it": ["information technology", " it "],
        "mechanical": ["mechanical", "mech"],
        "civil": ["civil"],
        "electronics": ["electronics", "e&tc", "entc"],
        "electrical": ["electrical", "eee"],
    }

    for key, aliases in branch_aliases.items():
        if key in preferred_lower:
            return any(alias in college_lower for alias in aliases)

    # Direct partial match fallback
    return preferred_lower[:5] in college_lower


def calculate_probability(student_pct: float, cutoff_pct: float, category: str) -> float:
    """
    Calculate admission probability as a percentage (0-100).
    
    Logic:
    - If student percentage > cutoff: high probability
    - Category-wise relaxation applied
    - Buffer zone of ±5% around cutoff
    """
    # Category-wise relaxation in percentile points
    category_relaxation = {
        "OPEN": 0,
        "OBC": 3,
        "SC": 10,
        "ST": 12,
        "EWS": 5
    }
    relaxation = category_relaxation.get(category.upper(), 0)
    effective_student_pct = student_pct + relaxation

    gap = effective_student_pct - cutoff_pct

    if gap >= 10:
        return 95.0    # Very safe
    elif gap >= 5:
        return 85.0    # Safe
    elif gap >= 2:
        return 70.0    # Likely target
    elif gap >= 0:
        return 55.0    # Borderline target
    elif gap >= -3:
        return 35.0    # Reach (dream)
    elif gap >= -6:
        return 20.0    # Tough reach
    else:
        return 8.0     # Very tough dream


def calculate_preference_score(student: Dict, college: Dict) -> int:
    """
    Score a college based on how well it matches student preferences.
    Max score: 100 points
    """
    score = 0

    # City preference (25 points)
    if student.get("preferred_city", "").lower() in college.get("city", "").lower():
        score += 25
    elif student.get("preferred_city", "") == "":
        score += 10   # No city preference = neutral

    # Budget match (25 points)
    student_budget = student.get("budget", 0)
    college_fees = college.get("fees", 0)
    if student_budget >= college_fees:
        # More budget headroom = better
        budget_ratio = (student_budget - college_fees) / max(student_budget, 1)
        score += int(budget_ratio * 25)

    # Government vs Private preference (20 points)
    if student.get("govt_preferred"):
        if college.get("type", "").lower() == "government":
            score += 20
    else:
        if college.get("type", "").lower() == "private":
            score += 10
        else:
            score += 5

    # Hostel availability (15 points)
    if student.get("hostel_needed") and college.get("hostel_available"):
        score += 15
    elif not student.get("hostel_needed"):
        score += 8   # Don't penalize if student doesn't need hostel

    # Placement priority (15 points)
    if student.get("placement_priority"):
        placement = college.get("placements_avg", 0)
        if placement >= 10:
            score += 15
        elif placement >= 7:
            score += 10
        elif placement >= 5:
            score += 5

    return min(score, 100)


def build_recommendation_card(college: Dict, probability: float, preference_score: int, student: Dict) -> Dict:
    """
    Build the final recommendation card object sent to frontend.
    """
    return {
        "name": college["name"],
        "branch": college["branch"],
        "city": college.get("city", "N/A"),
        "type": college.get("type", "N/A"),
        "fees": college.get("fees", 0),
        "fees_display": format_fees(college.get("fees", 0)),
        "cutoff_percentile": college.get("cutoff_percentile", 0),
        "placements_avg": college.get("placements_avg", 0),
        "naac_grade": college.get("naac_grade", "N/A"),
        "hostel_available": bool(college.get("hostel_available", 0)),
        "admission_probability": probability,
        "preference_score": preference_score,
        "match_label": get_match_label(probability),
        "latitude": college.get("latitude", 18.5204),
        "longitude": college.get("longitude", 73.8567)
    }


def format_fees(fees: int) -> str:
    """Convert raw fee number to readable string like ₹1.2L/year"""
    if fees >= 100000:
        return f"₹{fees/100000:.1f}L/year"
    elif fees >= 1000:
        return f"₹{fees/1000:.0f}K/year"
    return f"₹{fees}/year"


def get_match_label(probability: float) -> str:
    """Human-readable label for admission probability"""
    if probability >= 75:
        return "High Chance"
    elif probability >= 40:
        return "Good Chance"
    elif probability >= 20:
        return "Low Chance"
    return "Very Tough"