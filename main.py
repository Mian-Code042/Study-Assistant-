from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import logging
import traceback
from pathlib import Path
from rag import StudyAssistant
from database import init_db, save_document, save_history, get_all_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Study Assistant", version="1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

init_db()

assistant = StudyAssistant()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
current_document_id = None


def _safe_save_history(document_id, interaction_type: str, topic: str, question: str, content: str) -> None:
    """Persist history without breaking successful API responses."""
    try:
        save_history(
            document_id=document_id,
            interaction_type=interaction_type,
            topic=topic,
            question=question,
            content=content,
        )
    except Exception as e:
        logger.warning(f"History save failed ({interaction_type}): {e}")

class QuestionRequest(BaseModel):
    question: str

class GenerateRequest(BaseModel):
    topic: str = ""
    count: int = 5

# ====================== Upload ======================
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global current_document_id
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunk_count = assistant.process_pdf(str(file_path))
        current_document_id = save_document(file.filename, str(file_path), chunk_count)
        
        return {
            "message": "PDF processed successfully",
            "filename": file.filename,
            "chunks": chunk_count,
            "document_id": current_document_id
        }
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, str(e))

# ====================== Ask Question ======================
@app.post("/ask")
async def ask_question(req: QuestionRequest):
    global current_document_id
    try:
        if not req.question or not req.question.strip():
            raise HTTPException(status_code=400, detail="Question is required")

        answer = assistant.ask_question(req.question)

        _safe_save_history(current_document_id, "chat", "", req.question, answer)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ask error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))

# ====================== MCQs ======================
@app.post("/mcqs")
async def generate_mcqs(req: GenerateRequest):
    global current_document_id
    try:
        if not req.topic or not req.topic.strip():
            raise HTTPException(status_code=400, detail="Topic is required")

        mcqs = assistant.generate_mcqs(req.topic, req.count)

        _safe_save_history(current_document_id, "mcqs", req.topic, req.topic, mcqs)
        return {"mcqs": mcqs}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCQs error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))

# ====================== Flashcards ======================
@app.post("/flashcards")
async def generate_flashcards(req: GenerateRequest):
    global current_document_id
    try:
        if not req.topic or not req.topic.strip():
            raise HTTPException(status_code=400, detail="Topic is required")

        flashcards = assistant.generate_flashcards(req.topic, req.count)

        _safe_save_history(current_document_id, "flashcards", req.topic, req.topic, flashcards)
        return {"flashcards": flashcards}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Flashcards error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))

# ====================== History ======================
@app.get("/history")
async def get_history(limit: int = 50):
    try:
        history = get_all_history(limit=limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, str(e))