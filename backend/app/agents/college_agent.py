from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from ..config.config import settings
from ..rag.vector_store import vector_store_manager
from ..database.session import SessionLocal
from ..models.models import College, Cutoff, StudentProfile
from ..llm.groq_client import get_groq_llm
from sqlalchemy.orm import Session
import json

# Tools
@tool
def search_cutoffs(query: str):
    """Search for college cutoff information in the vector database."""
    docs = vector_store_manager.search(query, k=5)
    return "\n".join([doc.page_content for doc in docs])

@tool
def get_college_details(college_name: str):
    """Get detailed information about a specific college from the database."""
    db = SessionLocal()
    try:
        college = db.query(College).filter(College.name.ilike(f"%{college_name}%")).first()
        if college:
            return {
                "name": college.name,
                "location": college.location,
                "fees": college.fees,
                "placement": college.placement_record,
                "avg_package": college.avg_package,
                "hostel": college.hostel_available,
                "naac": college.naac_rating,
                "branches": college.branches
            }
        return "College not found."
    finally:
        db.close()

@tool
def recommend_colleges_tool(student_data: dict):
    """
    Generate college recommendations (Dream, Target, Safe) based on student rank, percentage, and category.
    Expected student_data keys: 'rank', 'percentage', 'category', 'preferred_branch'.
    """
    db = SessionLocal()
    try:
        rank = student_data.get('rank')
        category = student_data.get('category', 'Open')
        branch = student_data.get('preferred_branch', 'Computer Engineering')
        
        # Retrieval from Vector DB for historical context
        query = f"Cutoff for {branch} in {category} category around rank {rank}"
        historical_docs = vector_store_manager.search(query, k=5)
        context = "\n".join([doc.page_content for doc in historical_docs])
        
        llm = get_groq_llm()
        prompt = f"""
        Based on the following student data and historical cutoff context, provide 3-5 college recommendations.
        Student Data: {student_data}
        Historical Context: {context}
        
        Categorize recommendations into:
        1. Dream Colleges
        2. Target Colleges
        3. Safe Colleges
        
        Include probability of admission and reasoning for each.
        """
        response = llm.invoke(prompt)
        return response.content
    finally:
        db.close()

class CollegeAgent:
    def __init__(self):
        self.llm = get_groq_llm()
        self.tools = [search_cutoffs, get_college_details, recommend_colleges_tool]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional Engineering Admission Counselor in Pune.
            Your goal is to guide students through the admission process (DSE/CET).
            
            WORKFLOW:
            1. Check the 'Student Profile' provided in the context.
            2. If 'percentage' is missing, politely ask the student to upload their marksheet in the 'Document Center' or provide their percentage.
            3. If 'category' is missing, ask: "What is your category? (Open, OBC, SC, ST, or EWS)".
            4. If 'preferred_branch' is missing, ask: "Which engineering branch are you interested in? (e.g., Computer Engineering, IT, AI&DS, ENTC, Mechanical, Civil)".
            5. Ask if they are interested in "Pune only or all of Maharashtra?".
            6. Once you have the percentage, category, and branch, use the 'recommend_colleges_tool' to get recommendations.
            7. Present the recommendations as a top 10 list if possible, categorized into Dream, Target, and Safe.
            8. Be helpful, professional, and act like a real counselor.
            
            SESSION CONTEXT:
            Student Profile: {student_profile}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    async def chat(self, user_input: str, chat_history: list = None, student_profile: dict = None):
        if chat_history is None:
            chat_history = []
        
        response = await self.agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history,
            "student_profile": json.dumps(student_profile) if student_profile else "Not provided"
        })
        return response["output"]

college_agent = CollegeAgent()
