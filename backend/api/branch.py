"""
CollegePath AI — Branch Guidance API Router
"""
from fastapi import APIRouter
from backend.agents.branch_agent import BranchGuidanceAgent
from backend.api.schemas import BranchAnswers, BranchChatMessage, APIResponse

router = APIRouter(prefix="/api/branch", tags=["Branch Guidance"])
branch_agent = BranchGuidanceAgent()


@router.get("/questions")
async def get_branch_questions():
    """Get interest quiz questions for branch guidance."""
    return APIResponse(data=branch_agent.get_questions())


@router.post("/recommend")
async def recommend_branch(answers: BranchAnswers):
    """Get AI branch recommendations based on interest answers."""
    result = await branch_agent.recommend_branches(answers.model_dump())
    return APIResponse(data=result)


@router.post("/chat")
async def branch_chat(body: BranchChatMessage):
    """Open-ended chat about engineering branches."""
    response = await branch_agent.chat_about_branches(
        user_message=body.message,
        history=body.history,
    )
    return APIResponse(data={"response": response})
