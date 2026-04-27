import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ========================= CONFIG =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

# Initialize Groq LLM (Very Fast & Strong)
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",      # Best balance of speed & quality
    temperature=0.3,
    max_tokens=1024,
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True}
)

class StudyAssistant:
    def __init__(self):
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )

    def process_pdf(self, pdf_path: str) -> int:
        """Process and index a PDF"""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)
        
        self.vector_store = FAISS.from_documents(chunks, embeddings)
        
        # Save vector store
        Path("vectorstore").mkdir(exist_ok=True)
        self.vector_store.save_local("vectorstore")
        
        logger.info(f"✅ Processed {len(chunks)} chunks from PDF")
        return len(chunks)

    def ask_question(self, question: str, k: int = 5) -> str:
        if not self.vector_store:
            self.load_vectorstore()
        
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = ChatPromptTemplate.from_template(
            """You are an expert study assistant. Answer the question using ONLY the provided context.
            If the answer is not in the context, say "I don't have enough information from the document."

            Context:
            {context}

            Question: {question}
            Answer:"""
        )

        chain = prompt | llm
        response = chain.invoke({"context": context, "question": question})
        return response.content.strip()

    def generate_mcqs(self, topic: str, count: int = 5) -> str:
        if not self.vector_store:
            self.load_vectorstore()
        
        docs = self.vector_store.similarity_search(topic, k=6)
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = ChatPromptTemplate.from_template(
            """Generate {count} high-quality multiple choice questions from the context.
            Format each question like this:

            Q1: [Question]
            A) option1
            B) option2
            C) option3
            D) option4
            Correct: [Letter]

            Context: {context}"""
        )

        chain = prompt | llm
        response = chain.invoke({"context": context, "count": count})
        return response.content

    def generate_flashcards(self, topic: str, count: int = 5) -> str:
        if not self.vector_store:
            self.load_vectorstore()
        
        query = topic.strip() if topic and topic.strip() else "important concepts, definitions, and key facts"
        docs = self.vector_store.similarity_search(query, k=5)
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = ChatPromptTemplate.from_template(
            """Create {count} clean flashcards from the context.
            Return plain text only. Use this exact format:

            FRONT: [Term or Question]
            BACK: [Answer or Explanation]

            Separate each card with a blank line.

            Context: {context}"""
        )

        chain = prompt | llm
        response = chain.invoke({"context": context, "count": count})
        return response.content

    
    def load_vectorstore(self):
        if Path("vectorstore").exists():
            self.vector_store = FAISS.load_local(
                "vectorstore", 
                embeddings, 
                allow_dangerous_deserialization=True
            )
        else:
            raise ValueError("No vector store found. Please upload and process a PDF first.")