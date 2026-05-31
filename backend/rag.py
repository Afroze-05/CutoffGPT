"""
rag.py - RAG Chatbot (Retrieval Augmented Generation)
======================================================
HOW RAG WORKS (simple explanation):
  1. When admin uploads cutoff PDF → we split it into chunks → create embeddings → store in Pinecone
  2. When student asks a question → we create embedding of question → search Pinecone for similar chunks
  3. We send the relevant chunks + question to LLM (Gemini/Groq) → LLM answers using that context

This way, the chatbot only answers from actual uploaded data, not random guesses!

Setup:
  PINECONE_API_KEY=your_key in .env
  GEMINI_API_KEY=your_key in .env
  OR
  GROQ_API_KEY=your_key in .env
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

# ── Configuration ──────────────────────────────────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX_NAME", "collegepath")
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")

# ── Initialize Pinecone ────────────────────────────────────────────
pinecone_client = None
pinecone_index  = None

def init_pinecone():
    """
    Connect to Pinecone vector database.
    Called lazily (only when needed) to avoid startup errors.
    """
    global pinecone_client, pinecone_index
    if not PINECONE_API_KEY:
        print("⚠️ PINECONE_API_KEY not set - RAG will use fallback mode")
        return False

    try:
        from pinecone import Pinecone, ServerlessSpec

        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

        # Create index if it doesn't exist yet
        existing_indexes = [idx.name for idx in pinecone_client.list_indexes()]
        if PINECONE_INDEX not in existing_indexes:
            pinecone_client.create_index(
                name=PINECONE_INDEX,
                dimension=768,      # Google embedding dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"✅ Created Pinecone index: {PINECONE_INDEX}")

        pinecone_index = pinecone_client.Index(PINECONE_INDEX)
        print("✅ Pinecone connected successfully")
        return True

    except Exception as e:
        print(f"⚠️ Pinecone setup failed: {e}")
        return False


def store_pdf_chunks(pdf_path: str, colleges: List[Dict]):
    """
    Step 1 of RAG: Convert college data to text chunks and store in Pinecone.
    
    For each college record, we create a descriptive text chunk like:
    "PCCOE offers Computer Engineering with OPEN cutoff of 92.5 percentile.
     Annual fees are ₹1.2L. Average placement is 8 LPA. NAAC grade: A+"
    """
    if not init_pinecone():
        print("Skipping Pinecone storage - not configured")
        return

    # Create text chunks from college data
    chunks = []
    for i, college in enumerate(colleges):
        text = create_college_chunk(college)
        chunks.append({
            "id": f"college_{i}_{hash(text) % 10000}",
            "text": text,
            "metadata": {
                "name": college["name"],
                "branch": college["branch"],
                "city": college.get("city", ""),
                "cutoff": college.get("cutoff_percentile", 0)
            }
        })

    # Create embeddings and store in Pinecone
    try:
        embeddings = create_embeddings([c["text"] for c in chunks])
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": {"text": chunk["text"], **chunk["metadata"]}
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            pinecone_index.upsert(vectors=vectors[i:i+batch_size])

        print(f"✅ Stored {len(vectors)} chunks in Pinecone")

    except Exception as e:
        print(f"⚠️ Pinecone storage error: {e}")


def chat_with_rag(question: str, student_context: dict = {}) -> str:
    """
    Step 2 of RAG: Answer a student question using retrieved context.
    
    Process:
    1. Embed the question
    2. Search Pinecone for similar chunks
    3. Build a prompt with retrieved context
    4. Send to LLM and return answer
    """
    # Try RAG if Pinecone is configured
    context_text = ""
    if init_pinecone() and pinecone_index:
        context_text = retrieve_context(question)

    # If no Pinecone context, use fallback (sample data)
    if not context_text:
        context_text = get_fallback_context(question)

    # Build the full prompt for LLM
    prompt = build_rag_prompt(question, context_text, student_context)

    # Call LLM (Gemini or Groq)
    answer = call_llm(prompt)
    return answer


def retrieve_context(question: str, top_k: int = 5) -> str:
    """
    Search Pinecone for the most relevant college data chunks.
    Returns them as a single string context.
    """
    try:
        # Embed the question
        question_embedding = create_embeddings([question])[0]

        # Search Pinecone
        results = pinecone_index.query(
            vector=question_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Extract and join the relevant text chunks
        context_parts = []
        for match in results.matches:
            if match.score > 0.5:   # Only include relevant results
                context_parts.append(match.metadata.get("text", ""))

        return "\n".join(context_parts)

    except Exception as e:
        print(f"⚠️ Retrieval error: {e}")
        return ""


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create vector embeddings for a list of texts.
    Uses Google's text-embedding model (free tier available).
    Falls back to a simple hash-based vector if no API key.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)

        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            embeddings.append(result['embedding'])
        return embeddings

    except Exception as e:
        print(f"⚠️ Embedding error: {e}, using dummy embeddings")
        # Return dummy 768-dim vectors as fallback
        import random
        return [[random.uniform(-1, 1) for _ in range(768)] for _ in texts]


def build_rag_prompt(question: str, context: str, student_context: dict) -> str:
    """
    Build the prompt that combines question + retrieved context.
    This is sent to the LLM.
    """
    student_info = ""
    if student_context:
        student_info = f"""
Student Profile:
- Percentage: {student_context.get('percentage', 'N/A')}%
- Category: {student_context.get('category', 'N/A')}
- Preferred Branch: {student_context.get('preferred_branch', 'N/A')}
"""

    prompt = f"""You are CollegePath AI, a helpful college admission counselor for engineering colleges in Maharashtra, India.

Answer ONLY based on the provided context below. If the answer is not in the context, say "I don't have data for that. Please ask your college counselor."

Be friendly, specific, and helpful. Include college names, branch names, and cutoff percentiles when available.

{student_info}

COLLEGE DATA CONTEXT:
{context}

STUDENT QUESTION: {question}

Answer:"""

    return prompt


def call_llm(prompt: str) -> str:
    """
    Call Gemini or Groq LLM with the given prompt.
    Tries Gemini first, falls back to Groq, then to a hardcoded fallback.
    """
    # ── Try Gemini ─────────────────────────────────────────────────
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"⚠️ Gemini error: {e}")

    # ── Try Groq ───────────────────────────────────────────────────
    if GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ Groq error: {e}")

    # ── Fallback (No API Keys) ─────────────────────────────────────
    return get_fallback_answer(prompt)


def create_college_chunk(college: Dict) -> str:
    """
    Convert a college record dict into a descriptive text string for embedding.
    """
    return (
        f"{college['name']} offers {college['branch']} with "
        f"{college.get('category', 'OPEN')} category cutoff of "
        f"{college.get('cutoff_percentile', 'N/A')} percentile "
        f"(approximately rank {college.get('cutoff_rank', 'N/A')}). "
        f"Annual fees: ₹{college.get('fees', 0):,}. "
        f"Location: {college.get('city', 'N/A')}, {college.get('type', 'N/A')} college. "
        f"Average placement: {college.get('placements_avg', 0)} LPA. "
        f"NAAC Grade: {college.get('naac_grade', 'N/A')}. "
        f"Hostel: {'Available' if college.get('hostel_available') else 'Not Available'}."
    )


def get_fallback_context(question: str) -> str:
    """
    Fallback context when Pinecone is not configured.
    Returns relevant sample data as context.
    """
    from sample_data import SAMPLE_COLLEGES
    context_parts = [create_college_chunk(c) for c in SAMPLE_COLLEGES[:8]]
    return "\n".join(context_parts)


def get_fallback_answer(prompt: str) -> str:
    """Fallback answer when no LLM API is configured."""
    return (
        "I'm running in demo mode (no API keys configured). "
        "To enable full AI answers, add GEMINI_API_KEY or GROQ_API_KEY to your .env file. "
        "Based on our sample data: PCCOE, COEP, VIT Pune, and Symbiosis are top options "
        "for Computer Engineering in Pune with cutoffs ranging from 88-96 percentile."
    )