import streamlit as st
import requests
import re
import html
from textwrap import dedent
from database import init_db, get_all_history, search_history, clear_history

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

init_db()

# ── Session state ─────────────────────────────────────────────────────────────
if "processed" not in st.session_state:
    st.session_state.processed = False
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS Variables ── */
:root {
    --gold: #C9A84C;
    --gold-light: #E8C96A;
    --gold-pale: rgba(201,168,76,0.10);
    --gold-border: rgba(201,168,76,0.30);
    --gold-shadow: rgba(201,168,76,0.18);
}

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div {
    color: #0E1117 !important;
}
/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
header { visibility: visible; }
.stApp [data-testid="collapsedControl"] { display: flex !important; }

/* ── Main block container (light / system theme) ── */
.block-container {
    padding: 2rem 2.5rem 4rem 2.5rem;
    max-width: 1280px;
    background-color: transparent;
    margin-top: 1rem;
}  
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background-color: #0E1117;
}
/* ── SIDEBAR — always dark, immune to system theme ── */
section[data-testid="stSidebar"] {
    background: #0F0F12 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    color-scheme: dark;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.25rem;
    background-color: transparent !important;
    box-shadow: none;
    margin-top: 0;
}
/* Force all sidebar text to light colors */
section[data-testid="stSidebar"] * {
    color-scheme: dark;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: rgba(255,255,255,0.65) !important;
}

/* ── Sidebar logo area ── */
.sidebar-logo {
    text-align: center;
    padding: 1.5rem 0 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.75rem;
}
.sidebar-logo-icon {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: rgba(201,168,76,0.12);
    border: 1px solid rgba(201,168,76,0.28);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.85rem;
    font-size: 1.5rem;
}
.sidebar-logo h1 {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--gold) !important;
    margin: 0.2rem 0 0;
    letter-spacing: 0.02em;
}
.sidebar-logo p {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.28) !important;
    margin: 0.3rem 0 0;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}

/* ── Upload zone ── */
.upload-zone {
    background: rgba(201,168,76,0.05);
    border: 1px dashed rgba(201,168,76,0.32);
    border-radius: 14px;
    padding: 1.4rem 1rem;
    text-align: center;
    margin-bottom: 1rem;
    transition: all 0.25s ease;
    cursor: pointer;
}
.upload-zone:hover {
    border-color: var(--gold);
    background: rgba(201,168,76,0.09);
}
.upload-zone p {
    font-size: 0.75rem;
    color: var(--gold) !important;
    font-weight: 500;
    margin: 0.3rem 0 0;
}
.upload-zone span {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.28) !important;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 999px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.75rem;
}
.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: inline-block;
}
.status-pill-active {
    background: rgba(74,222,128,0.10);
    border-color: rgba(74,222,128,0.30);
    color: rgba(74,222,128,0.85) !important;
}
.status-dot-active {
    background: #4ade80;
    box-shadow: 0 0 6px rgba(74,222,128,0.6);
}

/* ── Sidebar divider ── */
.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 1.5rem 0;
}

/* ── Sidebar section label ── */
.sidebar-section-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22) !important;
    margin-bottom: 0.75rem;
    display: block;
    color: rgba(255, 255, 255, 0.55) !important;
}

/* ── Sidebar footer ── */
.sidebar-footer {
    font-size: 0.65rem;
    color: rgba(255,255,255,0.18) !important;
    line-height: 1.9;
    padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: auto;
}

/* ── Sidebar file uploader widget tweaks ── */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: rgba(201,168,76,0.05) !important;
    border: 1px dashed rgba(201,168,76,0.35) !important;
    border-radius: 14px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
    color: rgba(255,255,255,0.55) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: #1a1200 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    box-shadow: 0 4px 16px var(--gold-shadow) !important;
    padding: 0.6rem 1.2rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Page header ── */
.page-header {
    padding: 0.5rem 0 2rem;
    border-bottom: 1px solid rgba(0,0,0,0.07);
    margin-bottom: 2rem;
}
[data-theme="dark"] .page-header { border-bottom-color: rgba(255,255,255,0.07); }

.page-header h2 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: inherit;
    margin: 0 0 0.3rem;
    line-height: 1.15;
}
.page-header p {
    font-size: 0.9rem;
    margin: 0;
    opacity: 0.55;
    font-weight: 400;
}

/* ── Gold accent line ── */
.gold-line {
    height: 2.5px;
    width: 44px;
    background: linear-gradient(90deg, var(--gold), var(--gold-light));
    border-radius: 2px;
    margin: 0.5rem 0 0.85rem;
}

/* ── Stat cards ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 2rem;
}
.stat-card {
    padding: 1.1rem 1.25rem;
    border-radius: 14px;
    border: 1px solid rgba(0,0,0,0.07);
    background: rgba(0,0,0,0.02);
}
[data-theme="dark"] .stat-card {
    border-color: rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.03);
}
.stat-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.45;
    margin-bottom: 5px;
}
.stat-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--gold);
}
.stat-sub { font-size: 0.72rem; opacity: 0.45; margin-top: 2px; }

/* ── Tab overrides ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(0,0,0,0.08);
    gap: 0;
}
[data-theme="dark"] .stTabs [data-baseweb="tab-list"] {
    border-bottom-color: rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    opacity: 0.5;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.86rem;
    letter-spacing: 0.01em;
    padding: 0.75rem 1.4rem;
    border: none;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    opacity: 1 !important;
    border-bottom: 2px solid var(--gold) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover { opacity: 0.85 !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 2rem 0 0; }

/* ── Input fields & Selectbox ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: transparent !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 1.1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-theme="dark"] .stTextInput > div > div > input,
[data-theme="dark"] .stTextArea > div > div > textarea {
    border-color: rgba(255,255,255,0.10) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--gold-border) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    opacity: 0.4 !important;
}
.stTextInput label,
.stTextArea label,
.stSelectbox label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    opacity: 0.5 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div > div {
    background: transparent !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-theme="dark"] .stSelectbox > div > div > div {
    border-color: rgba(255,255,255,0.10) !important;
}
ul[data-baseweb="menu"] {
    border-radius: 12px !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
}

/* ── Main buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: #1a1200 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px var(--gold-shadow) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(201,168,76,0.3) !important;
    opacity: 0.92 !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary (danger) buttons like "Clear conversation" */
.stButton > button[kind="secondary"] {
    background-color: #0E1117 !important;
    color: inherit !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    box-shadow: none !important;
}
[data-theme="dark"] .stButton > button[kind="secondary"] {
    border-color: rgba(255,255,255,0.10) !important;
}

/* ── Chat messages ── */
.chat-bubble-user {
    background: rgba(0,0,0,0.03);
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 18px 18px 4px 18px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 3rem 0.75rem 5rem;
    font-size: 0.9rem;
    line-height: 1.65;
}
[data-theme="dark"] .chat-bubble-user {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.07);
}
.chat-bubble-ai {
    background: rgba(201,168,76,0.05);
    border: 1px solid rgba(201,168,76,0.22);
    border-radius: 18px 18px 18px 4px;
    padding: 1.2rem 1.5rem;
    margin: 0.75rem 5rem 0.75rem 0;
    font-size: 0.9rem;
    line-height: 1.75;
}
.chat-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.45;
}
.chat-label-user { text-align: right; margin-right: 3rem; }
.chat-label-ai { color: var(--gold) !important; opacity: 1 !important; margin-left: 0; }

/* ── Cards ── */
.mcq-card, .history-card, .controls-card, .flashcard {
    background: transparent;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
[data-theme="dark"] .mcq-card,
[data-theme="dark"] .history-card,
[data-theme="dark"] .controls-card,
[data-theme="dark"] .flashcard {
    border-color: rgba(255,255,255,0.07);
}

.mcq-option {
    background: rgba(0,0,0,0.02);
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin: 0.4rem 0;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.88rem;
}
[data-theme="dark"] .mcq-option {
    background: rgba(255,255,255,0.03);
    border-color: rgba(255,255,255,0.07);
}
.mcq-option:hover {
    border-color: var(--gold-border);
    background: var(--gold-pale);
}
.mcq-option.correct {
    background: rgba(74,222,128,0.07);
    border-color: rgba(74,222,128,0.35);
}
.option-letter {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.10);
    font-size: 0.72rem;
    font-weight: 700;
    flex-shrink: 0;
    background: rgba(0,0,0,0.03);
}
[data-theme="dark"] .option-letter {
    border-color: rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.05);
}
.mcq-correct-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 0.75rem;
    padding: 5px 14px;
    border-radius: 99px;
    background: rgba(74,222,128,0.10);
    border: 1px solid rgba(74,222,128,0.28);
    color: #15803d;
    font-size: 0.76rem;
    font-weight: 600;
}
[data-theme="dark"] .mcq-correct-badge { color: #4ade80; }

.mcq-number {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.6rem;
}
.mcq-question {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    line-height: 1.5;
}
.mcq-options { display: flex; flex-direction: column; gap: 6px; }

/* ── Flashcard ── */
.flashcard-grid { display: flex; flex-direction: column; gap: 14px; }
.flashcard { 
    overflow: hidden; 
    position: relative;
}
.flashcard-number {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--gold);
    opacity: 0.5;
    z-index: 10;
}
.flashcard-front {
    padding: 1.5rem 1.5rem 1.2rem;
    background: linear-gradient(135deg, rgba(201,168,76,0.08) 0%, rgba(201,168,76,0.12) 100%);
    border-bottom: 1px solid rgba(201,168,76,0.20);
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.flashcard-back { 
    padding: 1.5rem 1.5rem 1.2rem; 
    background: rgba(255,255,255,0.02);
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
[data-theme="dark"] .flashcard-back {
    background: rgba(255,255,255,0.03);
}
.flashcard-front-label, .flashcard-back-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    opacity: 0.5;
}
.flashcard-front-label { color: var(--gold); opacity: 1; }
.flashcard-back-label { color: #4ade80; opacity: 0.85; }
.flashcard-front-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    line-height: 1.6;
    color: inherit;
    font-weight: 600;
}
.flashcard-back-text {
    font-size: 0.92rem;
    line-height: 1.75;
    opacity: 0.85;
    color: inherit;
}

/* ── History card ── */
.history-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.75rem; }
.history-badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 99px;
    background: var(--gold-pale);
    border: 1px solid var(--gold-border);
    color: var(--gold);
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.history-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.98rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
    word-break: break-word;
}
.content-wrapper {
    max-height: 240px;
    overflow-y: auto;
    overflow-x: auto;
    padding-right: 0.35rem;
}
.history-text {
    font-size: 0.84rem;
    line-height: 1.65;
    opacity: 0.72;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.flash-container,
.mcq-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.flash-item {
    background: rgba(0,0,0,0.02);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}
[data-theme="dark"] .flash-item {
    background: rgba(255,255,255,0.02);
    border-color: rgba(255,255,255,0.06);
}
.flash-number {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--gold);
    opacity: 0.6;
    margin-bottom: 0.5rem;
}
.flash-section {
    margin-bottom: 0.75rem;
}
.flash-section:last-child {
    margin-bottom: 0;
}
.flash-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold);
    opacity: 0.8;
    display: block;
    margin-bottom: 0.4rem;
}
.flash-label.label-back {
    color: #4ade80;
}
.flash-divider {
    height: 1px;
    background: rgba(0,0,0,0.06);
    margin: 0.75rem 0;
}
[data-theme="dark"] .flash-divider {
    background: rgba(255,255,255,0.06);
}
.flash-content,
.mcq-line,
.mcq-correct {
    line-height: 1.65;
    font-size: 0.88rem;
}
.flash-content {
    color: inherit;
    opacity: 0.85;
}
.text-muted {
    opacity: 0.75;
}
.mcq-line {
    padding: 0.3rem 0;
    color: inherit;
}
.mcq-correct {
    background: rgba(74,222,128,0.08);
    border: 1px solid rgba(74,222,128,0.25);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    color: #15803d;
    font-weight: 600;
    margin-top: 0.5rem;
}
[data-theme="dark"] .mcq-correct {
    color: #4ade80;
}
.history-empty {
    text-align: center;
    padding: 3rem 1rem;
    opacity: 0.4;
    font-size: 0.9rem;
}

/* ── Section headings ── */
.section-heading {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.section-subtext { font-size: 0.85rem; opacity: 0.5; margin-bottom: 1.5rem; }

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3.5rem 2rem;
    border: 1px dashed rgba(0,0,0,0.10);
    border-radius: 18px;
    background: rgba(0,0,0,0.015);
    gap: 0.75rem;
    margin-top: 1rem;
}
[data-theme="dark"] .empty-state {
    border-color: rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
}
.empty-state-icon {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    border: 1px solid var(--gold-border);
    background: var(--gold-pale);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
}
.empty-state p { opacity: 0.5; font-size: 0.88rem; line-height: 1.65; margin: 0; }

/* ── Slider ── */
.stSlider [data-baseweb="slider"] { padding: 0; }
.stSlider [data-baseweb="thumb"] { background: var(--gold) !important; border-color: var(--gold) !important; }
.stSlider [data-baseweb="track-fill"] { background: var(--gold) !important; }

/* ── Answer card (fallback) ── */
.answer-card {
    padding: 1.25rem 1.5rem;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 14px;
    font-size: 0.9rem;
    line-height: 1.75;
    background: transparent;
}
[data-theme="dark"] .answer-card { border-color: rgba(255,255,255,0.07); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201,168,76,0.25); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(201,168,76,0.45); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — parse raw LLM text into structured data
# ─────────────────────────────────────────────────────────────────────────────

def parse_mcqs(raw: str) -> list[dict]:
    """Parse LLM MCQ output into structured list."""
    mcqs = []
    blocks = re.split(r'(?=(?:Q\d*[:\.]|^\d+[\.)])\s)', raw, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q_match = re.search(r'(?:Q\d*[:.]\s*|^\d+[.)]\s*)(.+?)(?=\n[A-D][.):]|\nA[.):])', block, re.DOTALL)
        if not q_match:
            continue
        question = q_match.group(1).strip()
        opts = {}
        for letter in ['A', 'B', 'C', 'D']:
            m = re.search(rf'{letter}[.):\s]+(.+?)(?=\n[A-D][.):\s]|Correct|Answer|$)', block, re.DOTALL | re.IGNORECASE)
            if m:
                opts[letter] = m.group(1).strip()
        correct_match = re.search(r'(?:Correct|Answer)[:\s]+([A-D])', block, re.IGNORECASE)
        correct = correct_match.group(1).upper() if correct_match else ""
        if question and opts:
            mcqs.append({"question": question, "options": opts, "correct": correct})
    return mcqs


def parse_flashcards(raw: str) -> list[dict]:
    """Robust flashcard parser - works with Groq output"""
    cards = []
    lines = raw.strip().split('\n')
    front = None
    back = []
    front_marker = re.compile(r'(?i)^(?:FRONT|QUESTION)\s*[:\-.)]\s*|^Q\s*[:\-.)]\s*')
    back_marker = re.compile(r'(?i)^(?:BACK|ANSWER)\s*[:\-.)]\s*|^A\s*[:\-.)]\s*')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if front_marker.match(line):
            if front and back:
                cards.append({"front": front, "back": "\n".join(back).strip()})
            front = front_marker.sub('', line).strip()
            back = []
        elif back_marker.match(line):
            content = back_marker.sub('', line).strip()
            if content:
                back.append(content)
        elif front is not None:
            back.append(line)
    if front and back:
        cards.append({"front": front, "back": "\n".join(back).strip()})
    if not cards:
        pattern = re.findall(
            r'(?i)(?:FRONT|QUESTION)[:\s\-]*(.+?)(?:BACK|ANSWER)[:\s\-]*(.+?)(?=(?:FRONT|QUESTION)|$)',
            raw, re.DOTALL
        )
        cards = [{"front": f.strip(), "back": b.strip()} for f, b in pattern if f.strip() and b.strip()]
    return cards


def format_flashcard_text(text: str) -> str:
    """Clean and format flashcard text, removing HTML tags and escaping properly."""
    if not text:
        return ""
    # Remove any HTML tags that might be in the text
    text = re.sub(r'<[^>]+>', '', text)
    # Escape HTML entities
    text = html.escape(text)
    # Convert newlines to breaks
    text = text.replace("\n\n", "<br><br>")
    text = text.replace("\n", "<br>")
    return text


def render_flashcards(raw: str):
    cards = parse_flashcards(raw)
    if not cards:
        cleaned = format_flashcard_text(raw)
        st.markdown(f'<div class="answer-card">{cleaned}</div>', unsafe_allow_html=True)
        return
    
    st.markdown(f'<p class="section-subtext">{len(cards)} flashcards generated</p>', unsafe_allow_html=True)
    
    cards_html = '<div class="flashcard-grid">'
    for i, card in enumerate(cards, 1):
        front = format_flashcard_text(card['front'])
        back = format_flashcard_text(card['back'])
        cards_html += dedent(f"""
        <div class="flashcard">
            <div class="flashcard-number">#{i:02d}</div>
            <div class="flashcard-front">
                <div class="flashcard-front-label">◆ FRONT</div>
                <div class="flashcard-front-text">{front}</div>
            </div>
            <div class="flashcard-back">
                <div class="flashcard-back-label">◈ BACK</div>
                <div class="flashcard-back-text">{back}</div>
            </div>
        </div>
        """)
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def render_mcqs(raw: str):
    mcqs = parse_mcqs(raw)
    if not mcqs:
        st.markdown(f'<div class="answer-card">{raw}</div>', unsafe_allow_html=True)
        return
    st.markdown(f'<p class="section-subtext">{len(mcqs)} question{"s" if len(mcqs)>1 else ""} generated from your document</p>', unsafe_allow_html=True)
    for i, mcq in enumerate(mcqs, 1):
        opts_html = ""
        for letter, text in mcq["options"].items():
            is_correct = letter == mcq["correct"]
            cls = "mcq-option correct" if is_correct else "mcq-option"
            opts_html += f'<div class="{cls}"><span class="option-letter">{letter}</span>{text}</div>'
        correct_html = ""
        if mcq["correct"] and mcq["correct"] in mcq["options"]:
            correct_html = f'<div class="mcq-correct-badge">✓ Correct: {mcq["correct"]} — {mcq["options"].get(mcq["correct"], "")}</div>'
        st.markdown(f"""
        <div class="mcq-wrapper">
            <div class="mcq-card">
                <div class="mcq-number">Question {i:02d}</div>
                <div class="mcq-question">{mcq['question']}</div>
                <div class="mcq-options">{opts_html}</div>
                {correct_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


def load_history_records(record_type: str = "all", topic: str = "", query: str = "", limit: int = 20) -> list[dict]:
    base_records = search_history(query=query.strip(), limit=max(limit, 200)) if query.strip() else get_all_history(limit=max(limit, 200))
    filtered_records = []
    topic_lower = topic.strip().lower()
    for item in base_records:
        item_type = (item.get("type") or item.get("interaction_type") or "").lower()
        item_topic = (item.get("topic") or "").lower()
        if record_type != "all" and item_type != record_type:
            continue
        if topic_lower and topic_lower not in item_topic:
            continue
        filtered_records.append(item)
    return filtered_records[:limit]


def sanitize_history_text(content: str) -> str:
    """Remove old HTML/template fragments from saved history payloads."""
    text = html.unescape(str(content or ""))
    text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', text)
    text = re.sub(r'(?s)<[^>]+>', '', text)
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned_lines = [line for line in lines if line.strip()]
    return "\n".join(cleaned_lines).strip()


def format_history_content(content):
    content_str = sanitize_history_text(content)
    
    # 1. Handle Flashcards (FRONT/BACK)
    if "FRONT:" in content_str.upper() and "BACK:" in content_str.upper():
        cards = parse_flashcards(content_str)
        if cards:
            cards_html = '<div class="flash-container">'
            for idx, card in enumerate(cards, 1):
                front = format_flashcard_text(card.get("front", ""))
                back = format_flashcard_text(card.get("back", ""))
                cards_html += dedent(f'''
                <div class="flash-item">
                    <div class="flash-number">Card #{idx:02d}</div>
                    <div class="flash-section">
                        <span class="flash-label">FRONT</span>
                        <div class="flash-content">{front}</div>
                    </div>
                    <div class="flash-divider"></div>
                    <div class="flash-section">
                        <span class="flash-label label-back">BACK</span>
                        <div class="flash-content text-muted">{back}</div>
                    </div>
                </div>
                ''')
            cards_html += '</div>'
            return cards_html

    # 2. Handle MCQs
    elif "Q1:" in content_str or "A)" in content_str:
        # Highlight the Correct answer line
        lines = content_str.split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "Correct:" in line:
                formatted_lines.append(f'<div class="mcq-correct"><b>✔</b> {html.escape(line)}</div>')
            else:
                formatted_lines.append(f'<div class="mcq-line">{html.escape(line)}</div>')
        return f'<div class="mcq-container">{"".join(formatted_lines)}</div>'

    # 3. Default Fallback
    return f'<div class="history-text">{html.escape(content_str)}</div>'
# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🧠</div>
        <h1>StudyMind</h1>
        <p>AI · Powered · Learning</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-section-label">Your Document</span>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        if st.button("⚡  Process PDF", use_container_width=True):
            with st.spinner("Analyzing document..."):
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.session_state.processed = True
                        st.session_state.doc_name = uploaded_file.name
                        st.success("Document ready!")
                    else:
                        st.error("Processing failed. Is the backend running?")
                except Exception:
                    st.error("Cannot reach backend. Run: uvicorn main:app --reload")

    if st.session_state.processed:
        name = st.session_state.doc_name[:26] + ("…" if len(st.session_state.doc_name) > 26 else "")
        st.markdown(f"""
        <div class="status-pill status-pill-active">
            <span class="status-dot status-dot-active"></span> {name}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-pill">
            <span class="status-dot"></span> No document loaded
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-footer">
        Built with LangChain · FAISS · Gemini<br>FastAPI · Streamlit
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main content
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h2>Your AI Study Companion</h2>
    <div class="gold-line"></div>
    <p>Upload any PDF and instantly get answers, quizzes, and flashcards powered by AI</p>
</div>
""", unsafe_allow_html=True)

# ── Stat cards ────────────────────────────────────────────────────────────────
questions_asked = len(st.session_state.chat_history)
st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-label">Questions Asked</div>
        <div class="stat-val">{questions_asked if questions_asked else "—"}</div>
        <div class="stat-sub">{"This session" if questions_asked else "Upload to begin"}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Document Status</div>
        <div class="stat-val">{"✓" if st.session_state.processed else "—"}</div>
        <div class="stat-sub">{"Indexed & ready" if st.session_state.processed else "No document yet"}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">AI Engine</div>
        <div class="stat-val" style="font-size:1.1rem;padding-top:4px">Gemini</div>
        <div class="stat-sub">LangChain · FAISS</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["  💬  Ask Questions  ", "  ❓  MCQ Quiz  ", "  📇  Flashcards  ", "  🕘  History  "])

# ── Tab 1: Ask Questions ──────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-heading">Ask Anything</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtext">Questions are answered exclusively from your uploaded document</p>', unsafe_allow_html=True)

    for entry in st.session_state.chat_history:
        st.markdown(f'<p class="chat-label chat-label-user">You</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-user">{entry["q"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="chat-label chat-label-ai">StudyMind</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-ai">{entry["a"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1], gap="small")
    with col1:
        question = st.text_input("", placeholder="e.g. Explain the difference between a stack and a queue", label_visibility="collapsed", key="q_input")
    with col2:
        ask_btn = st.button("Ask →", use_container_width=True)

    if ask_btn and question:
        if not st.session_state.processed:
            st.warning("Upload and process a PDF first using the sidebar.")
        else:
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(f"{API_URL}/ask", json={"question": question})
                    if r.status_code == 200:
                        answer = r.json()["answer"]
                        st.session_state.chat_history.append({"q": question, "a": answer})
                        st.rerun()
                    else:
                        st.error("Something went wrong. Please try again.")
                except Exception:
                    st.error("Cannot reach backend.")

    if not st.session_state.chat_history and not st.session_state.processed:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <p>Upload a PDF from the sidebar, then ask questions here.<br>
            The AI will answer only from your document.</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()


# ── Tab 2: MCQs ───────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-heading">Multiple Choice Quiz</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtext">Auto-generated questions with highlighted correct answers</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1], gap="medium")
    with col1:
        topic = st.text_input("Topic", placeholder="e.g. data structures, operating systems, databases", key="mcq_topic")
    with col2:
        count = st.slider("Questions", min_value=3, max_value=10, value=5, key="mcq_count")

    gen_mcq = st.button("⚡  Generate Quiz", key="gen_mcq_btn")

    if gen_mcq:
        if not st.session_state.processed:
            st.warning("Upload and process a PDF first.")
        elif not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner(f"Crafting {count} questions on '{topic}'..."):
                try:
                    r = requests.post(f"{API_URL}/mcqs", json={"topic": topic, "count": count})
                    if r.status_code == 200:
                        raw = r.json()["mcqs"]
                        render_mcqs(raw)
                    else:
                        st.error("Failed to generate MCQs.")
                except Exception:
                    st.error("Cannot reach backend.")

    if not gen_mcq and not st.session_state.processed:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">❓</div>
            <p>Enter a topic and generate a quiz from your PDF.<br>
            Correct answers are highlighted in green.</p>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 3: Flashcards ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-heading">Flashcard Deck</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtext">Review key concepts in a clean, scannable card format</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1], gap="medium")
    with col1:
        f_topic = st.text_input("Topic", placeholder="e.g. Python basics, machine learning, web development", key="fc_topic")
    with col2:
        f_count = st.slider("Cards", min_value=3, max_value=10, value=5, key="fc_count")

    gen_fc = st.button("✦  Generate Flashcards", key="gen_fc_btn")

    if gen_fc:
        if not st.session_state.processed:
            st.warning("Upload and process a PDF first.")
        elif not f_topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner(f"Building {f_count} flashcards on '{f_topic}'..."):
                try:
                    r = requests.post(f"{API_URL}/flashcards", json={"topic": f_topic, "count": f_count})
                    if r.status_code == 200:
                        raw = r.json()["flashcards"]
                        render_flashcards(raw)
                    else:
                        st.error("Failed to generate flashcards.")
                except Exception:
                    st.error("Cannot reach backend.")

    if not gen_fc and not st.session_state.processed:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📇</div>
            <p>Enter a topic and generate beautiful flashcards from your document.<br>
            Each card shows the question on front and answer on back.</p>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 4: History ────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-heading">Saved History</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtext">Search saved chats, MCQs, and flashcards by type, topic, or text</p>', unsafe_allow_html=True)

    st.markdown('<div class="controls-card">', unsafe_allow_html=True)
    h_col1, h_col2, h_col3, h_col4 = st.columns([1, 1, 1, 0.7], gap="medium")
    with h_col1:
        history_type = st.selectbox(
            "Type",
            options=["all", "chat", "mcqs", "flashcards"],
            format_func=lambda value: "All" if value == "all" else value.upper(),
            key="history_type",
        )
    with h_col2:
        history_topic = st.text_input("Topic", placeholder="e.g. data structures", key="history_topic")
    with h_col3:
        history_query = st.text_input("Search", placeholder="e.g. stack, queue, recursion", key="history_query")
    with h_col4:
        history_limit = st.slider("Limit", min_value=5, max_value=100, value=20, step=5, key="history_limit")
    st.markdown('</div>', unsafe_allow_html=True)

    action_col1, action_col2 = st.columns([1, 1], gap="small")
    with action_col1:
        search_clicked = st.button("Search History", key="history_search_btn")
    with action_col2:
        clear_clicked = st.button("Clear History", key="history_clear_btn")

    if clear_clicked:
        removed = clear_history()
        st.success(f"Cleared {removed} history item{'s' if removed != 1 else ''}.")
        st.rerun()

    if search_clicked:
        history_results = load_history_records(
            record_type=history_type,
            topic=history_topic,
            query=history_query,
            limit=history_limit,
        )
    else:
        history_results = load_history_records(limit=history_limit)

    if not history_results:
        st.markdown('<div class="history-empty">No saved items match your filters yet.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="section-subtext">{len(history_results)} saved item{"s" if len(history_results) != 1 else ""} shown</p>', unsafe_allow_html=True)
        for item in history_results:
            item_type = item.get("type") or item.get("interaction_type") or "item"
            item_topic = item.get("topic") or "general"
            item_document = item.get("document") or item.get("filename") or "Unknown document"
            item_timestamp = item.get("timestamp") or item.get("created_at") or ""
            item_question = item.get("question") or item_topic
            item_content = item.get("content") or ""

            st.markdown(
                f'''
                <div class="history-card">
                    <div class="history-meta">
                        <span class="history-badge type-badge">{html.escape(str(item_type).upper())}</span>
                        <span class="history-badge">{html.escape(str(item_topic))}</span>
                        <span class="history-badge">{html.escape(str(item_document))}</span>
                        <span class="history-badge time-badge">{html.escape(str(item_timestamp))}</span>
                    </div>
                    <div class="history-title">{html.escape(str(item_question))}</div>
                    <div class="content-wrapper">
                        {format_history_content(item_content)}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )