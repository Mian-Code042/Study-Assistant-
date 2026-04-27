```markdown
# Study Assistant - RAG Project

A powerful PDF-based Retrieval-Augmented Generation (RAG) assistant using LangChain, FAISS, and Google Gemini.

---

## How to Run (Super Easy)

### Step 1: Clone or Download the Project
Download or extract the project folder.

### Step 2: Create Virtual Environment

Open **PowerShell** in the project folder and run:

```powershell
python -m venv venv
```

### Step 3: Activate the Environment

```powershell
.\venv\Scripts\Activate.ps1
```

> **If activation fails**, run this command first:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 4: Install All Dependencies

```powershell
pip install -r requirements.txt
```

### Step 5: Add Your Gemini API Key

1. Create a new file named `.env` in the root folder.
2. Add the following line:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 6: Run the Application

- **Using FastAPI** (Recommended):
  ```powershell
  uvicorn main:app --reload
  ```

- **Using Streamlit**:
  ```powershell
  streamlit run app.py
  ```

---

## Project Structure

```
study-assistant/
├── venv/                  # Virtual environment (auto-created)
├── requirements.txt
├── .env                   # (Create this)
├── rag.py                 # RAG logic
├── main.py                # FastAPI backend
├── app.py                 # Streamlit version (optional)
├── vectorstore/           # Saved FAISS index (auto-created)
├── setup.bat              # Optional one-click setup
└── README.md
```

---

**You're all set!** 🎉

Just follow the steps above and the project should run smoothly for anyone.

---

pip install langchain-groq

