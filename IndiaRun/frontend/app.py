import os
# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import json
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

try:
    # pyrefly: ignore [missing-import]
    import plotly.express as px
    # pyrefly: ignore [missing-import]
    import plotly.graph_objects as go
    import pandas as pd
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


# Load environments
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

# Page Configuration
st.set_page_config(
    page_title="TalentPool | AI Recruiter Hub",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Custom CSS Styling (Glassmorphism, Dark Accents, Gradients, Cards & Custom Typography)
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background color */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Custom Title Gradient Header */
    .header-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .header-title {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .header-subtitle {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #3b82f6;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Candidate Match Card */
    .candidate-card {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: all 0.2s ease;
    }
    .candidate-card:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
    }
    .candidate-name {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    .candidate-score-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .candidate-score-badge-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .candidate-meta {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .candidate-meta span {
        margin-right: 15px;
    }
    
    /* Skill Pill */
    .skill-pill {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 0.1rem 0.6rem;
        margin: 2px 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Styled lists for screening */
    .pros-list li {
        color: #a7f3d0;
        margin-bottom: 0.3rem;
    }
    .cons-list li {
        color: #fca5a5;
        margin-bottom: 0.3rem;
    }
    .q-list li {
        color: #e0f2fe;
        margin-bottom: 0.5rem;
        font-style: italic;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper functions to talk to FastAPI backend
def fetch_candidates():
    try:
        response = requests.get(f"{BACKEND_URL}/candidates/")
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def delete_candidate(cid):
    try:
        response = requests.delete(f"{BACKEND_URL}/candidates/{cid}")
        return response.status_code == 200
    except Exception:
        return False

def render_recruiter_explanation(rep: dict):
    expl = rep.get("recruiter_explanation") or {}
    if not expl:
        return
    
    st.markdown("---")
    st.markdown("#### 💬 Executive Recruiter Explanation")
    
    # Rationale banner
    st.info(f"**🎯 Placement & Ranking Rationale**\n\n{expl.get('why_this_ranking', 'N/A')}")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown(f"**📈 Career Trajectory & Velocity**\n\n{expl.get('career_progression', 'N/A')}")
        st.markdown(f"**🛠️ Missing Skills Operational Impact**\n\n{expl.get('missing_skills_impact', 'N/A')}")
    with col_e2:
        st.markdown(f"**💼 Projected Business & Team Value**\n\n{expl.get('business_impact', 'N/A')}")
        st.markdown(f"**🔍 Evaluation Confidence Rationale**\n\n{expl.get('confidence_rationale', 'N/A')}")
        
    ev_highlights = expl.get("evidence_highlights") or []
    if ev_highlights:
        st.write("")
        st.markdown("**📄 Key Resume Evidence References:**")
        for h in ev_highlights:
            st.markdown(f"- <span style='font-size: 0.85rem; font-style: italic; color: #cbd5e1;'>\"{h}\"</span>", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">TalentPool AI Recruiter Hub</h1>
        <p class="header-subtitle">Streamlined semantic parsing, intelligent job description matching, and candidate screening report generation</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation
st.sidebar.markdown("<h2 style='color: white; font-weight: 600;'>Navigation</h2>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Go to",
    ["💼 Recruiter Workspace", "💬 Recruiter Chat", "📈 Talent Analytics", "Dashboard & Upload", "Semantic Search & Match", "Job Analyzer", "Candidate Screening & Chat"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: white; font-weight: 500;'>Service Connections</h3>", unsafe_allow_html=True)
st.sidebar.text(f"API Target:\n{BACKEND_URL}")

# Check backend status
try:
    health_check = requests.get(f"{BACKEND_URL}/").json()
    st.sidebar.success("Backend: Connected ✅")
except Exception:
    st.sidebar.error("Backend: Disconnected ❌")
    health_check = {"indexed_candidates": 0}

# ----------------- PAGE 0: RECRUITER WORKSPACE -----------------
if page == "💼 Recruiter Workspace":
    st.markdown("### 💼 Unified Recruiter Workspace")
    st.write("A high-productivity workspace combining resume uploads, semantic/hybrid matching, and deep-dive multi-agent evaluations in a unified page layout.")
    
    # 1. Left Panel / Sidebar inputs
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📝 Job Description Details")
    
    workspace_jd = st.sidebar.text_area(
        "Job Description Text", 
        height=180, 
        placeholder="Paste target job description to match against...",
        key="workspace_jd"
    )
    
    # Analyze Job Description button
    if st.sidebar.button("⚙️ Parse Job Description", use_container_width=True):
        if not workspace_jd.strip():
            st.sidebar.warning("Please paste a Job Description first.")
        else:
            with st.sidebar.spinner("Parsing job profile..."):
                try:
                    job_payload = {"job_description": workspace_jd}
                    job_resp = requests.post(f"{BACKEND_URL}/jobs/analyze", json=job_payload)
                    if job_resp.status_code == 200:
                        st.session_state.workspace_job_profile = job_resp.json()
                        st.sidebar.success("Job description successfully parsed!")
                    else:
                        st.sidebar.error("Failed to parse Job Description.")
                except Exception as e:
                    st.sidebar.error(f"Error parsing job description: {str(e)}")
                    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📤 Upload Resumes")
    
    uploaded_files = st.sidebar.file_uploader(
        "Upload files (.pdf, .docx)", 
        accept_multiple_files=True,
        key="workspace_uploader"
    )
    
    if st.sidebar.button("🚀 Upload & Index Resumes", use_container_width=True):
        if not uploaded_files:
            st.sidebar.warning("Select files to upload first.")
        else:
            success_count = 0
            fail_count = 0
            for uploaded_file in uploaded_files:
                with st.sidebar.spinner(f"Ingesting {uploaded_file.name}..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        resp = requests.post(f"{BACKEND_URL}/candidates/upload", files=files)
                        if resp.status_code == 200:
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception:
                        fail_count += 1
            if success_count > 0:
                st.sidebar.success(f"Uploaded {success_count} resumes! (Failed: {fail_count})")
            else:
                st.sidebar.error("Failed to ingest any resumes. Check backend logs.")
                
    # 2. Main Workspace layout (Center & Right Columns)
    col_center, col_right = st.columns([4.5, 5.5])
    
    # Initialize session state cache keys
    if "workspace_matches" not in st.session_state:
        st.session_state.workspace_matches = []
    if "workspace_selected_cand" not in st.session_state:
        st.session_state.workspace_selected_cand = None
    if "workspace_job_profile" not in st.session_state:
        st.session_state.workspace_job_profile = None
        
    with col_center:
        st.markdown("#### 🎯 Matching Candidates")
        search_mode = st.radio(
            "Matcher Algorithm", 
            ["Standard Semantic", "🔍 Intelligent Hybrid Matcher (Composite)"], 
            horizontal=True,
            key="workspace_match_mode"
        )
        
        top_n = st.slider("Results Count", min_value=1, max_value=20, value=5, key="workspace_top_n")
        
        if st.button("🎯 Run Matching Engine", use_container_width=True):
            if not workspace_jd.strip():
                st.warning("Please paste the Job Description in the left sidebar.")
            else:
                endpoint = "/search/hybrid" if "Hybrid" in search_mode else "/search/match"
                with st.spinner("Screening candidates..."):
                    try:
                        payload = {"query": workspace_jd, "top_n": top_n}
                        response = requests.post(f"{BACKEND_URL}{endpoint}", json=payload)
                        if response.status_code == 200:
                            st.session_state.workspace_matches = response.json().get("results", [])
                            st.success(f"Matched {len(st.session_state.workspace_matches)} candidates!")
                        else:
                            st.error("Failed to query match endpoint.")
                    except Exception as e:
                        st.error(f"Error connecting to backend matches: {str(e)}")
                        
        # Render candidate cards list
        if st.session_state.workspace_matches:
            for idx, match in enumerate(st.session_state.workspace_matches):
                cand = match.get("candidate", {})
                is_hybrid = "Hybrid" in search_mode
                score = match.get("composite_score" if is_hybrid else "score", 0.0)
                percentage = int(score * 100)
                
                badge_class = "candidate-score-badge" if percentage >= 70 else "candidate-score-badge-medium"
                badge_text = f"{percentage}% Hybrid" if is_hybrid else f"{percentage}% Match"
                
                # Checkbox selection simulated by buttons
                card_bg = "rgba(30, 41, 59, 0.9)"
                is_selected = st.session_state.workspace_selected_cand and st.session_state.workspace_selected_cand.get("id") == cand.get("id")
                card_border = "1px solid #3b82f6" if is_selected else "1px solid rgba(255, 255, 255, 0.05)"
                
                st.markdown(
                    f"""
                    <div style="background: {card_bg}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: {card_border};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="candidate-name">#{idx+1} {cand.get('name') or 'N/A'}</div>
                            <div class="{badge_class}">{badge_text}</div>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                            <span>⏳ {cand.get('experience_years', 0.0)} Yrs Exp</span> | <span>🎓 {cand.get('education') or 'N/A'}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # In order to inspect, click a select button
                if st.button(f"🔍 Evaluate {cand.get('name')}", key=f"select_cand_{cand.get('id')}"):
                    st.session_state.workspace_selected_cand = cand
                    st.rerun()
        else:
            st.caption("No candidates matched yet. Paste a Job Description and click 'Run Matching Engine'.")
            
    with col_right:
        st.markdown("#### 👤 Candidate Deep-Dive Evaluation")
        
        selected_cand = st.session_state.workspace_selected_cand
        if not selected_cand:
            st.info("Select a candidate from the matching list to inspect their profile and run deep evaluations.")
        else:
            st.markdown(f"### {selected_cand.get('name')}")
            
            # Brief metadata tags
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.02); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                        <span>📧 {selected_cand.get('email') or 'N/A'}</span>
                        <span>📞 {selected_cand.get('phone') or 'N/A'}</span>
                        <span>⏳ {selected_cand.get('experience_years', 0.0)} Yrs Exp</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Render skills
            skills = selected_cand.get("skills", [])
            skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
            st.markdown(f"<div style='margin-bottom: 15px;'>{skills_html}</div>", unsafe_allow_html=True)
            
            # --- EVALUATION AGENT PANELS ---
            cand_id = selected_cand.get("id")
            
            # Check for parsed job profile in state
            job_profile = st.session_state.workspace_job_profile
            
            # 1. Stage-2 Re-ranking Fit Report
            st.markdown("---")
            st.markdown("##### 🔍 Deep Re-Ranking Fit & Hiring Recommendation")
            
            if not job_profile:
                st.caption("⚠️ Please click '⚙️ Parse Job Description' in the sidebar to enable deep fit analysis.")
            else:
                rerank_key = f"workspace_rerank_{cand_id}"
                if rerank_key not in st.session_state:
                    st.session_state[rerank_key] = None
                    
                if st.button("⚡ Run Stage-2 LLM Re-Ranking", key=f"btn_rerank_{cand_id}", use_container_width=True):
                    with st.spinner("Analyzing profile alignment..."):
                        try:
                            rerank_payload = {
                                "candidate_id": cand_id,
                                "job_profile": job_profile
                            }
                            rerank_resp = requests.post(f"{BACKEND_URL}/search/rerank", json=rerank_payload)
                            if rerank_resp.status_code == 200:
                                st.session_state[rerank_key] = rerank_resp.json()
                            else:
                                st.error("Failed to run deep profile re-ranking.")
                        except Exception as e:
                            st.error(f"Error querying re-ranking API: {str(e)}")
                            
                if st.session_state[rerank_key] is not None:
                    rep = st.session_state[rerank_key]
                    score = rep.get("overall_score", 0)
                    rec = rep.get("hiring_recommendation", "N/A")
                    conf = rep.get("confidence", 0.0)
                    
                    score_color = "#10b981" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")
                    rec_color = "#10b981" if "Hire" in rec and "No" not in rec else "#ef4444"
                    
                    st.markdown(
                        f"""
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                            <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;">
                                <span style="font-size: 1.8rem; font-weight: 800; color: {score_color};">{score}%</span><br/>
                                <span style="font-size: 0.8rem; color: #94a3b8;">LLM Fit Score (Conf: {conf:.2f})</span>
                            </div>
                            <div style="background: rgba(30, 41, 59, 0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;">
                                <span style="font-size: 1.1rem; font-weight: 700; color: {rec_color}; text-transform: uppercase;">{rec}</span><br/>
                                <span style="font-size: 0.8rem; color: #94a3b8;">Hiring Recommendation</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    c_str, c_wk = st.columns(2)
                    with c_str:
                        st.markdown("**👍 Key Strengths:**")
                        for s in rep.get("strengths", []):
                            st.markdown(f"- <span style='font-size: 0.85rem;'>{s}</span>", unsafe_allow_html=True)
                    with c_wk:
                        st.markdown("**⚠️ Risks / Gaps:**")
                        for w in rep.get("weaknesses", []):
                            st.markdown(f"- <span style='font-size: 0.85rem;'>{w}</span>", unsafe_allow_html=True)
                            
                    # Recruiter Explanation details
                    render_recruiter_explanation(rep)
                            
            # 2. Evidence Verification quotes
            st.markdown("---")
            st.markdown("##### 🧬 Resume Evidence Verification Agent")
            
            evidence_key = f"workspace_evidence_{cand_id}"
            if evidence_key not in st.session_state:
                st.session_state[evidence_key] = None
                
            col_ev_btn, col_ev_input = st.columns([1.5, 2])
            with col_ev_input:
                verify_input = st.text_input(
                    "Skills/Traits to verify (comma-separated)", 
                    value="Leadership, Python, Cloud" if skills else "Leadership",
                    key=f"verify_input_{cand_id}"
                )
            with col_ev_btn:
                st.write("") # spacing
                run_evidence = st.button("🧬 Verify Evidence", key=f"btn_evidence_{cand_id}", use_container_width=True)
                
            if run_evidence:
                topics = [t.strip() for t in verify_input.split(",") if t.strip()]
                if not topics:
                    st.warning("Please provide at least one skill/topic to verify.")
                else:
                    with st.spinner("Extracting verbatim resume evidence..."):
                        try:
                            payload = {"candidate_id": cand_id, "topics": topics}
                            resp = requests.post(f"{BACKEND_URL}/candidates/evidence", json=payload)
                            if resp.status_code == 200:
                                st.session_state[evidence_key] = resp.json().get("evidence", {})
                            else:
                                st.error("Failed to extract evidence.")
                        except Exception as e:
                            st.error(f"Error querying evidence API: {str(e)}")
                            
            if st.session_state[evidence_key] is not None:
                evidence_data = st.session_state[evidence_key]
                for topic, quote in evidence_data.items():
                    if quote:
                        st.markdown(
                            f"""
                            <div style="background: rgba(16, 185, 129, 0.03); padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #10b981; font-size: 0.85rem;">
                                <strong>🔑 {topic}:</strong> <span style="font-style: italic; color: #e2e8f0;">"{quote}"</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="background: rgba(239, 68, 68, 0.03); padding: 8px; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid #ef4444; font-size: 0.85rem; color: #94a3b8;">
                                <strong>❌ {topic}:</strong> No direct matching quote evidence found.
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            # 3. Custom Interview Planner question lists
            st.markdown("---")
            st.markdown("##### 📋 Custom Interview Guide Planner")
            
            if not job_profile:
                st.caption("⚠️ Please click '⚙️ Parse Job Description' in the sidebar to enable interview guide planning.")
            else:
                planner_key = f"workspace_planner_{cand_id}"
                if planner_key not in st.session_state:
                    st.session_state[planner_key] = None
                    
                if st.button("📋 Compile Interview Guide", key=f"btn_planner_{cand_id}", use_container_width=True):
                    with st.spinner("Generating custom questions guide..."):
                        try:
                            planner_payload = {
                                "candidate_id": cand_id,
                                "job_profile": job_profile
                            }
                            planner_resp = requests.post(f"{BACKEND_URL}/search/interview-plan", json=planner_payload)
                            if planner_resp.status_code == 200:
                                st.session_state[planner_key] = planner_resp.json()
                            else:
                                st.error("Failed to generate interview guide.")
                        except Exception as e:
                            st.error(f"Error querying interview planner: {str(e)}")
                            
                if st.session_state[planner_key] is not None:
                    plan_guide = st.session_state[planner_key]
                    
                    st.write("")
                    st.markdown("**📡 Technical Questions:**")
                    for q in (plan_guide.get("technical_questions") or [])[:3]:
                        st.markdown(f"- <span style='font-size: 0.85rem;'>{q}</span>", unsafe_allow_html=True)
                        
                    st.markdown("**🧠 Behavioral & Cultural Questions:**")
                    for q in (plan_guide.get("behavioral_questions") or [])[:2]:
                        st.markdown(f"- <span style='font-size: 0.85rem;'>{q}</span>", unsafe_allow_html=True)
                        
                    st.markdown("**🛠️ Missing Skills / Gaps Questions:**")
                    for q in (plan_guide.get("missing_skills_questions") or [])[:2]:
                        st.markdown(f"- <span style='font-size: 0.85rem;'>{q}</span>", unsafe_allow_html=True)

# ----------------- PAGE 0.5: RECRUITER CHAT -----------------
if page == "💬 Recruiter Chat":
    st.markdown("### 💬 TalentPool Recruiter Chat")
    st.write("Converse with the recruiting AI assistant regarding the entire candidate pool, compare candidates, check missing skills, leadership capability, and explore what-if hiring scenarios.")
    
    # Text area for job description context in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📝 Job Context")
    chat_jd = st.sidebar.text_area(
        "Job Description Context (Optional)",
        value=st.session_state.get("workspace_jd", ""),
        height=200,
        placeholder="Paste a Job Description here to help focus the chat evaluations...",
        key="chat_jd"
    )
    
    # Setup session state for chat history
    state_key = "recruiter_chat_history"
    if state_key not in st.session_state:
        st.session_state[state_key] = []
        
    # Render chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state[state_key]:
            # Add a welcome message if history is empty
            st.session_state[state_key].append({
                "role": "assistant",
                "content": (
                    "Hello! I am your TalentPool recruiting assistant. I have full visibility of all indexed candidate profiles. "
                    "Feel free to ask me questions like:\n\n"
                    "- *'Why should we hire Candidate X over Y?'*\n"
                    "- *'Who has the strongest leadership credentials in our database?'*\n"
                    "- *'Which candidates have gaps in Kubernetes or cloud skills?'*\n"
                    "- *'Re-rank our profiles if AWS experience becomes an optional nice-to-have.'*"
                )
            })
            
        for msg in st.session_state[state_key]:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            bg_color = "rgba(59, 130, 246, 0.1)" if msg["role"] == "user" else "rgba(30, 41, 59, 0.4)"
            st.markdown(
                f"""
                <div style="background: {bg_color}; padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <span style="font-size: 1.2rem; margin-right: 8px;">{role_icon}</span>
                    <strong>{'You' if msg['role'] == 'user' else 'Recruiter Assistant'}:</strong>
                    <p style="margin: 5px 0 0 0; white-space: pre-wrap; font-size: 0.95rem;">{msg['content']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
    # Input box
    user_msg = st.chat_input("Ask about candidate comparisons, leadership, missing skills, etc.")
    if user_msg:
        st.session_state[state_key].append({"role": "user", "content": user_msg})
        
        # Prepare payload
        payload = {
            "message": user_msg,
            "history": st.session_state[state_key][:-1],
            "job_description": chat_jd if chat_jd.strip() else None
        }
        
        with st.spinner("Analyzing candidate pool..."):
            try:
                response = requests.post(f"{BACKEND_URL}/search/chat-recruiter", json=payload)
                if response.status_code == 200:
                    reply = response.json().get("reply", "")
                    st.session_state[state_key].append({"role": "assistant", "content": reply})
                    st.rerun()
                else:
                    st.error("Failed to query recruiter assistant API.")
            except Exception as e:
                st.error(f"Error querying recruiter chat: {str(e)}")

# ----------------- PAGE 0.7: TALENT ANALYTICS -----------------
if page == "📈 Talent Analytics":
    st.markdown("### 📈 Pool Visual Analytics Dashboard")
    st.write("Visual dashboard showing aggregate pool statistics, top skill trends, experience distributions, target industries, and evaluated talent gaps.")
    
    candidates = fetch_candidates()
    if not candidates:
        st.info("No candidates indexed yet. Please upload resume files under 'Dashboard & Upload' or in the 'Recruiter Workspace' sidebar.")
    elif not HAS_PLOTLY:
        st.warning("⚠️ Visual analytics library (Plotly / Pandas) not installed. Interactive charts are disabled. Please run 'pip install plotly pandas' in your environment to view charts.")
    else:
        # Prepare charts data
        
        # 1. Experience Binning
        exp_bins = {"0-2 Years": 0, "3-5 Years": 0, "6-8 Years": 0, "9+ Years": 0}
        for c in candidates:
            exp_yrs = c.get("experience_years") or 0.0
            if exp_yrs <= 2:
                exp_bins["0-2 Years"] += 1
            elif exp_yrs <= 5:
                exp_bins["3-5 Years"] += 1
            elif exp_yrs <= 8:
                exp_bins["6-8 Years"] += 1
            else:
                exp_bins["9+ Years"] += 1
                
        df_exp = pd.DataFrame(list(exp_bins.items()), columns=["Experience Bracket", "Candidate Count"])
        
        # 2. Skill Frequency Distribution
        skill_counts = {}
        for c in candidates:
            for skill in c.get("skills", []):
                s = skill.strip()
                if s:
                    # Title case to group duplicates
                    s_title = s.title()
                    skill_counts[s_title] = skill_counts.get(s_title, 0) + 1
                    
        df_skills = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"]).sort_values(by="Count", ascending=True).tail(15)
        
        # 3. Top Industries (Keyword Scanning)
        industries_list = ["Software", "Technology", "Finance", "Banking", "Healthcare", "Medical", "E-commerce", "Retail", "Education", "Consulting", "Automotive", "Energy"]
        industry_counts = {}
        for c in candidates:
            text = ((c.get("parsed_text") or "") + " " + (c.get("experience") or "")).lower()
            matched = False
            for ind in industries_list:
                if ind.lower() in text:
                    industry_counts[ind] = industry_counts.get(ind, 0) + 1
                    matched = True
            if not matched:
                industry_counts["Other / General"] = industry_counts.get("Other / General", 0) + 1
                
        df_ind = pd.DataFrame(list(industry_counts.items()), columns=["Industry Sector", "Count"]).sort_values(by="Count", ascending=False)
        
        # Render Analytics Row 1: Average Match Rate & Top Industries
        col_g1, col_g2 = st.columns([4, 6])
        
        with col_g1:
            st.markdown("##### 🎯 Average Match Rate Gauge")
            workspace_matches = st.session_state.get("workspace_matches", [])
            avg_score = 0.0
            if workspace_matches:
                scores = [m.get("score" if "score" in m else "composite_score", 0.0) for m in workspace_matches]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=int(avg_score * 100),
                number={'suffix': "%", 'font': {'size': 40}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#3b82f6"},
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.15)"},
                        {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.15)"},
                        {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.15)"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.caption("Average suitability rating of matched candidates against target active job description.")
            
        with col_g2:
            st.markdown("##### 🏢 Industry Domain Distribution")
            fig_pie = px.pie(df_ind, values="Count", names="Industry Sector", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.write("")
        
        # Render Analytics Row 2: Skill Distribution & Experience Distribution
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("##### 📊 Top 15 Pool Skills")
            fig_skills = px.bar(df_skills, x="Count", y="Skill", orientation="h", color="Count", color_continuous_scale="Viridis")
            fig_skills.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, coloraxis_showscale=False)
            st.plotly_chart(fig_skills, use_container_width=True)
            
        with col_c2:
            st.markdown("##### ⏳ Years of Experience Distribution")
            fig_exp = px.bar(df_exp, x="Experience Bracket", y="Candidate Count", color="Experience Bracket", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_exp.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, showlegend=False)
            st.plotly_chart(fig_exp, use_container_width=True)
            
        # Render Analytics Row 3: Missing Skill Trends (Talent Gaps)
        st.write("")
        st.markdown("##### 🛠️ Talent Gaps: Most Common Missing Skills")
        
        # Cross reference active job required skills against candidate pool
        job_profile = st.session_state.get("workspace_job_profile", {})
        req_skills_list = job_profile.get("required_skills", [])
        
        if not req_skills_list:
            st.info("💡 Paste a Job Description and click '⚙️ Parse Job Description' in the Recruiter Workspace sidebar to view the Gaps / Missing Skill Trends chart.")
        else:
            missing_counts = {}
            for c in candidates:
                cand_skills = {s.lower().strip() for s in c.get("skills", [])}
                for req in req_skills_list:
                    req_clean = req.lower().strip()
                    # If candidate doesn't have it (direct or substring match)
                    if not any(req_clean in cand or cand in req_clean for cand in cand_skills):
                        missing_counts[req] = missing_counts.get(req, 0) + 1
                        
            if not missing_counts:
                st.success("✅ The candidate pool matches all required skills for this job description!")
            else:
                df_missing = pd.DataFrame(list(missing_counts.items()), columns=["Required Skill", "Missing Count"]).sort_values(by="Missing Count", ascending=True)
                
                fig_missing = px.bar(df_missing, x="Missing Count", y="Required Skill", orientation="h", color="Missing Count", color_continuous_scale="Reds")
                fig_missing.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, coloraxis_showscale=False)
                st.plotly_chart(fig_missing, use_container_width=True)
                st.caption("How many candidates in the pool lack each specific required skill. Higher bars represent critical hiring target deltas.")

# ----------------- PAGE 1: DASHBOARD & UPLOAD -----------------
if page == "Dashboard & Upload":
    st.markdown("### 📊 Pool Overview & Ingestion")
    
    # Fetch candidates list
    candidates = fetch_candidates()
    
    # Overview Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(candidates)}</div>
                <div class="metric-label">Total Indexed Profiles</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        # Calculate avg experience
        avg_exp = sum(c.get("experience_years") or 0.0 for c in candidates) / len(candidates) if candidates else 0.0
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{avg_exp:.1f} Yrs</div>
                <div class="metric-label">Avg Candidate Experience</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        # Count parsing successes
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{health_check.get('indexed_candidates', 0)}</div>
                <div class="metric-label">FAISS Vector Count</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    st.write("")
    st.write("")

    # Resume Upload Section
    st.markdown("#### 📂 Import New Resumes")
    uploaded_files = st.file_uploader(
        "Drag and drop PDF or DOCX resume documents here", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🚀 Process & Index Uploads", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.write(f"Processing ({i+1}/{len(uploaded_files)}): **{uploaded_file.name}**...")
                
                # Send multipart upload request to backend
                files_payload = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post(f"{BACKEND_URL}/candidates/upload", files=files_payload)
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        st.error(f"Error parsing {uploaded_file.name}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend when uploading {uploaded_file.name}: {str(e)}")
                
                # Update progress
                progress_bar.progress(int(((i + 1) / len(uploaded_files)) * 100))
                
            status_text.success(f"Successfully processed and indexed **{success_count}** of **{len(uploaded_files)}** resumes!")
            st.rerun()

    st.write("")
    st.write("")
    
    # Profiles list with delete functionality
    st.markdown("#### 👤 Registered Candidates")
    if not candidates:
        st.info("No candidates registered. Please upload resumes above.")
    else:
        for c in candidates:
            with st.container():
                c_col1, c_col2 = st.columns([5, 1])
                skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in c.get("skills", [])])
                
                with c_col1:
                    st.markdown(
                        f"""
                        <div class="candidate-card" style="margin-bottom: 0px;">
                            <div class="candidate-name">{c.get('name') or 'N/A'}</div>
                            <div class="candidate-meta">
                                <span>📧 {c.get('email') or 'N/A'}</span>
                                <span>📞 {c.get('phone') or 'N/A'}</span>
                                <span>⏳ {c.get('experience_years', 0.0)} Yrs Exp</span>
                                <span>🎓 {c.get('education') or 'N/A'}</span>
                            </div>
                            <div style="margin-top: 8px;">
                                {skills_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_col2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Remove", key=f"del_{c.get('id')}", use_container_width=True):
                        if delete_candidate(c.get("id")):
                            st.success(f"Deleted {c.get('name')}")
                            st.rerun()
                        else:
                            st.error("Failed to delete candidate")
            st.write("")

# ----------------- PAGE 2: SEMANTIC MATCHING -----------------
elif page == "Semantic Search & Match":
    st.markdown("### 🔍 Candidate Matching Engine")
    st.write("Input a Job Description or search query to find candidates. Choose standard semantic lookup or hybrid multi-dimensional ranking.")
    
    job_desc = st.text_area("Job Description / Search Query", height=200, placeholder="We are looking for a Senior Python Developer with 5+ years of experience with FastAPI, Postgresql, and Docker. Experience with OpenAI API or LLMs is a plus...")
    
    col_mode, col_n = st.columns([3, 1])
    with col_mode:
        search_mode = st.radio("Search Match Algorithm", ["Standard Semantic Similarity", "🔍 Intelligent Hybrid Matcher (Composite)"], horizontal=True)
    with col_n:
        top_n = st.slider("Max Results to Display", min_value=1, max_value=20, value=5)
        
    st.write("")
    match_clicked = st.button("🎯 Find Matching Candidates", use_container_width=True)
        
    if match_clicked:
        if not job_desc.strip():
            st.warning("Please enter a job description or query first.")
        else:
            is_hybrid = "Hybrid" in search_mode
            endpoint = "/search/hybrid" if is_hybrid else "/search/match"
            
            with st.spinner("Processing match query and scoring candidates..."):
                payload = {"query": job_desc, "top_n": top_n}
                try:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", json=payload)
                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        
                        if not results:
                            st.info("No matching candidates found.")
                        else:
                            st.success(f"Found {len(results)} matches!")
                            for idx, match in enumerate(results):
                                cand = match.get("candidate", {})
                                
                                # Setup badges depending on search mode
                                if is_hybrid:
                                    score = match.get("composite_score", 0.0)
                                    sem_score = match.get("semantic_score", 0.0)
                                    skill_score = match.get("skill_score", 0.0)
                                    exp_score = match.get("experience_score", 0.0)
                                    ind_score = match.get("industry_score", 0.0)
                                    
                                    percentage = int(score * 100)
                                    badge_class = "candidate-score-badge" if percentage >= 70 else "candidate-score-badge-medium"
                                    badge_text = f"{percentage}% Hybrid Fit"
                                    
                                    score_breakdown_html = f"""
                                    <div style="margin-top: 10px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 0.8rem; color: #94a3b8;">
                                        <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);">
                                            <strong>📡 Semantic</strong><br/>
                                            <span style="color: #60a5fa; font-weight: 600; font-size: 0.95rem;">{int(sem_score*100)}%</span>
                                        </div>
                                        <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);">
                                            <strong>🛠️ Skills</strong><br/>
                                            <span style="color: #34d399; font-weight: 600; font-size: 0.95rem;">{int(skill_score*100)}%</span>
                                        </div>
                                        <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);">
                                            <strong>⏳ Experience</strong><br/>
                                            <span style="color: #f59e0b; font-weight: 600; font-size: 0.95rem;">{int(exp_score*100)}%</span>
                                        </div>
                                        <div style="background: rgba(255, 255, 255, 0.03); padding: 8px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);">
                                            <strong>🏢 Industry</strong><br/>
                                            <span style="color: #ec4899; font-weight: 600; font-size: 0.95rem;">{int(ind_score*100)}%</span>
                                        </div>
                                    </div>
                                    """
                                else:
                                    score = match.get("score", 0.0)
                                    percentage = int(score * 100)
                                    badge_class = "candidate-score-badge" if percentage >= 75 else "candidate-score-badge-medium"
                                    badge_text = f"{percentage}% Match"
                                    score_breakdown_html = ""
                                
                                skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in cand.get("skills", [])])
                                
                                st.markdown(
                                    f"""
                                    <div class="candidate-card">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div class="candidate-name">#{idx+1} {cand.get('name') or 'N/A'}</div>
                                            <div class="{badge_class}">{badge_text}</div>
                                        </div>
                                        <div class="candidate-meta">
                                            <span>📧 {cand.get('email') or 'N/A'}</span>
                                            <span>📞 {cand.get('phone') or 'N/A'}</span>
                                            <span>⏳ {cand.get('experience_years', 0.0)} Yrs Exp</span>
                                            <span>🎓 {cand.get('education') or 'N/A'}</span>
                                        </div>
                                        <div style="margin-top: 8px;">
                                            {skills_html}
                                        </div>
                                        {score_breakdown_html}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                except Exception as e:
                    st.error(f"Error querying backend matches: {str(e)}")

# ----------------- PAGE 3: JOB ANALYZER -----------------
elif page == "Job Analyzer":
    st.markdown("### 📋 Job Understanding Agent")
    st.write("Extract and structure skills, requirements, responsibilities, and deal-breakers from any raw job description.")
    
    raw_jd = st.text_area(
        "Job Description Raw Text", 
        height=250, 
        placeholder="Paste your raw job description here to extract requirements..."
    )
    
    if st.button("🔍 Analyze Job Description", use_container_width=True):
        if not raw_jd.strip():
            st.warning("Please enter a job description first.")
        else:
            with st.spinner("Analyzing job description via GPT..."):
                try:
                    payload = {"job_description": raw_jd}
                    response = requests.post(f"{BACKEND_URL}/jobs/analyze", json=payload)
                    if response.status_code == 200:
                        analysis = response.json()
                        
                        st.success("Analysis complete!")
                        
                        # Top Metrics Bar
                        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                        with m_col1:
                            st.info(f"💼 **Role:**\n\n{analysis.get('role') or 'N/A'}")
                        with m_col2:
                            st.info(f"📈 **Seniority:**\n\n{analysis.get('seniority') or 'N/A'}")
                        with m_col3:
                            st.info(f"⏳ **Min Experience:**\n\n{analysis.get('years_experience', 0.0)} Years")
                        with m_col4:
                            st.info(f"🎓 **Education:**\n\n{analysis.get('education') or 'N/A'}")
                            
                        # Double column split
                        col_l, col_r = st.columns(2)
                        
                        with col_l:
                            st.markdown("##### 🔑 Must Haves")
                            must_haves = analysis.get("must_have") or []
                            if must_haves:
                                for item in must_haves:
                                    st.markdown(f"- {item}")
                            else:
                                st.caption("None extracted.")
                                
                            st.markdown("##### 🛠️ Required Skills & Tools")
                            req_skills = analysis.get("required_skills") or []
                            tools = analysis.get("tools") or []
                            all_req = list(set(req_skills + tools))
                            if all_req:
                                for item in all_req:
                                    st.markdown(f"<span class='skill-pill'>{item}</span>", unsafe_allow_html=True)
                            else:
                                st.caption("None extracted.")
                            st.write("")
                            
                            st.markdown("##### 📋 Core Responsibilities")
                            resps = analysis.get("responsibilities") or []
                            if resps:
                                for item in resps:
                                    st.markdown(f"- {item}")
                            else:
                                st.caption("None extracted.")
                                
                        with col_r:
                            st.markdown("##### ⚠️ Deal Breakers")
                            deal_breakers = analysis.get("deal_breakers") or []
                            if deal_breakers:
                                for item in deal_breakers:
                                    st.markdown(f"<span style='color: #ef4444; font-weight: 500;'>🚨 {item}</span>", unsafe_allow_html=True)
                            else:
                                st.caption("None extracted.")
                                
                            st.markdown("##### ✨ Nice to Have / Preferred")
                            nice_to_haves = analysis.get("nice_to_have") or []
                            pref_skills = analysis.get("preferred_skills") or []
                            all_pref = list(set(nice_to_haves + pref_skills))
                            if all_pref:
                                for item in all_pref:
                                    st.markdown(f"- {item}")
                            else:
                                st.caption("None extracted.")
                                
                            st.markdown("##### 🧠 Behavioral Traits")
                            traits = analysis.get("behavioral_traits") or []
                            if traits:
                                for item in traits:
                                    st.markdown(f"- {item}")
                            else:
                                st.caption("None extracted.")
                    else:
                        st.error("Failed to analyze job description. Please check logs.")
                except Exception as e:
                    st.error(f"Error communicating with jobs analysis API: {str(e)}")

# ----------------- PAGE 4: SCREENING & CHAT -----------------
elif page == "Candidate Screening & Chat":
    st.markdown("### 🤖 Candidate Deep Dive & Screening")
    st.write("Generate a tailored candidate analysis and engage in an interactive screening conversation powered by their resume context.")
    
    candidates = fetch_candidates()
    
    if not candidates:
        st.info("No candidates available. Please upload resumes on the Dashboard.")
    else:
        # Candidate select box
        candidate_options = {f"{c.get('name')} ({c.get('email')})": c for c in candidates}
        selected_key = st.selectbox("Select Candidate to Evaluate", options=list(candidate_options.keys()))
        selected_cand = candidate_options[selected_key]
        
        # Sub tabs
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📄 Profile Details", "🧠 AI Competency Analysis", "🔍 Stage-2 Re-Ranking", "🛠️ Skill Gap Analysis", "📋 Interview Planner", "📝 Screening Report", "💬 Chat with Resume"])
        
        with tab0:
            st.markdown(f"#### 👤 {selected_cand.get('name') or 'N/A'} - Profile Overview")
            
            # Sub-metrics
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1:
                st.info(f"⏳ **Experience:** {selected_cand.get('experience_years', 0.0)} Years")
            with c_m2:
                st.info(f"🎓 **Education:** {selected_cand.get('education') or 'N/A'}")
            with c_m3:
                st.info(f"📞 **Phone:** {selected_cand.get('phone') or 'N/A'}")
                
            st.markdown("##### 💼 Experience Summary")
            st.write(selected_cand.get('experience') or "No summary parsed.")
            
            # Grid for details
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("##### 👔 Work History")
                work_history = selected_cand.get("work_history") or []
                if work_history:
                    for work in work_history:
                        st.markdown(f"- {work}")
                else:
                    st.caption("No work history listed.")
                    
                st.markdown("##### 📁 Key Projects")
                projects = selected_cand.get("projects") or []
                if projects:
                    for proj in projects:
                        st.markdown(f"- {proj}")
                else:
                    st.caption("No projects listed.")
                    
            with col_right:
                st.markdown("##### 📜 Certifications")
                certifications = selected_cand.get("certifications") or []
                if certifications:
                    for cert in certifications:
                        st.markdown(f"- {cert}")
                else:
                    st.caption("No certifications listed.")
                    
                st.markdown("##### 🏆 Achievements")
                achievements = selected_cand.get("achievements") or []
                if achievements:
                    for ach in achievements:
                        st.markdown(f"- {ach}")
                else:
                    st.caption("No achievements listed.")

            # Evidence Verification Agent section
            st.markdown("---")
            st.markdown("### 🧬 Resume Evidence Verification Agent")
            st.write("Verify any skill, project, or trait by extracting the exact sentence or passage from the candidate's raw resume.")
            
            # Options from candidate's parsed skills
            cand_skills = selected_cand.get("skills", [])
            
            col_v1, col_v2 = st.columns([2, 1])
            with col_v1:
                verify_skills = st.multiselect(
                    "Select parsed skills to verify", 
                    options=cand_skills,
                    default=cand_skills[:3] if cand_skills else []
                )
            with col_v2:
                custom_verify = st.text_input(
                    "Add custom topic (e.g. Leadership)", 
                    placeholder="Python, Kubernetes, etc..."
                )
                
            # Merge topics
            verify_topics = list(verify_skills)
            if custom_verify.strip():
                # Split by commas if they enter multiple custom ones
                custom_parts = [c.strip() for c in custom_verify.split(",") if c.strip()]
                verify_topics.extend(custom_parts)
                
            if st.button("🔍 Extract Resume Evidence Proof", use_container_width=True):
                if not verify_topics:
                    st.warning("Please select or type at least one topic to verify.")
                else:
                    with st.spinner("Forensically auditing resume and extracting exact quotes..."):
                        payload = {
                            "candidate_id": selected_cand.get("id"),
                            "topics": verify_topics
                        }
                        try:
                            response = requests.post(f"{BACKEND_URL}/candidates/evidence", json=payload)
                            if response.status_code == 200:
                                evidence_data = response.json().get("evidence", {})
                                
                                st.write("")
                                st.markdown("##### 📄 Extracted Proof & Quotes")
                                
                                for topic, quote in evidence_data.items():
                                    with st.container():
                                        if quote:
                                            st.markdown(
                                                f"""
                                                <div style="background: rgba(16, 185, 129, 0.05); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #10b981;">
                                                    <strong style="color: #34d399;">🔑 {topic}</strong><br/>
                                                    <p style="margin: 5px 0 0 0; font-style: italic; color: #e2e8f0;">"{quote}"</p>
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )
                                        else:
                                            st.markdown(
                                                f"""
                                                <div style="background: rgba(239, 68, 68, 0.05); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444;">
                                                    <strong style="color: #f87171;">❌ {topic}</strong><br/>
                                                    <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 0.85rem;">No direct matching evidence/quote found in candidate's resume.</p>
                                                </div>
                                                """,
                                                unsafe_allow_html=True,
                                            )
                            else:
                                st.error("Failed to run evidence extraction. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error connecting to backend services: {str(e)}")

        with tab1:
            st.markdown("#### 🧠 Deep Competency & Soft Skills Assessment")
            st.write("Generate a multi-dimensional assessment of the candidate's technical strengths, soft skills, growth potential, and overall alignment.")
            
            cand_id = selected_cand.get("id")
            cache_key = f"competency_analysis_{cand_id}"
            
            # Check session state for cached analysis
            if cache_key not in st.session_state:
                st.session_state[cache_key] = None
                
            if st.button("⚡ Run Competency Assessment", use_container_width=True) or st.session_state[cache_key] is not None:
                if st.session_state[cache_key] is None:
                    with st.spinner("Analyzing candidate profile via GPT..."):
                        try:
                            response = requests.post(f"{BACKEND_URL}/candidates/analyze/{cand_id}")
                            if response.status_code == 200:
                                st.session_state[cache_key] = response.json()
                            else:
                                st.error("Failed to run competency assessment. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error communicating with backend analysis service: {str(e)}")
                            
                if st.session_state[cache_key] is not None:
                    analysis = st.session_state[cache_key]
                    
                    st.success("Competency assessment generated!")
                    
                    st.markdown(f"**Career Trajectory Summary:**\n{analysis.get('career_summary')}")
                    
                    col_l, col_r = st.columns(2)
                    with col_l:
                        st.markdown("##### 🛠️ Core Technical Strengths")
                        techs = analysis.get("technical_strengths") or []
                        if techs:
                            tech_pills = "".join([f"<span class='skill-pill'>{t}</span>" for t in techs])
                            st.markdown(tech_pills, unsafe_allow_html=True)
                        else:
                            st.caption("None identified.")
                        st.write("")
                        
                        st.markdown("##### 👥 Leadership & Mentoring")
                        st.write(analysis.get("leadership") or "No direct leadership markers analyzed.")
                        
                        st.markdown("##### 🗣️ Communication & Alignment")
                        st.write(analysis.get("communication") or "No distinct communication markers analyzed.")
                        
                    with col_r:
                        st.markdown("##### 💼 Industry & Domain Exposure")
                        inds = analysis.get("industry_experience") or []
                        if inds:
                            for ind in inds:
                                st.markdown(f"- {ind}")
                        else:
                            st.caption("None identified.")
                            
                        st.markdown("##### 🧠 Behavioral & Cultural Traits")
                        traits = analysis.get("behavioral_traits") or []
                        if traits:
                            trait_pills = "".join([f"<span class='skill-pill' style='background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.3);'>{trait}</span>" for trait in traits])
                            st.markdown(trait_pills, unsafe_allow_html=True)
                        else:
                            st.caption("None identified.")
                        st.write("")
                        
                        st.markdown("##### 🎯 Ownership & Agency")
                        st.write(analysis.get("ownership") or "No distinct ownership markers analyzed.")
                        
                    st.markdown("##### 📈 Career Growth & Velocity")
                    st.write(analysis.get("career_growth") or "No distinct career velocity markers analyzed.")
                    
                    st.markdown("##### 🧠 Problem Solving & Analytical Style")
                    st.write(analysis.get("problem_solving") or "No distinct analytical style markers analyzed.")
                    
                    st.markdown(
                        f"""
                        <div style="background: rgba(30, 41, 59, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.2); margin-top: 1.5rem;">
                            <h5 style="color: #60a5fa; margin-top: 0px;">📋 Executive Summary</h5>
                            <p style="margin: 0px; line-height: 1.5;">{analysis.get('overall_summary')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab2:
            st.markdown("#### 🔍 Stage-2 Deep LLM Re-Ranking Fit Analysis")
            st.write("Perform a deep comparison between the candidate's parsed profile and a target Job Description to generate fit recommendations and confidence ratings.")
            
            rerank_jd = st.text_area(
                "Target Job Description", 
                height=150, 
                placeholder="Paste the target job description to run the deep re-ranking fit analysis...",
                key="rerank_jd"
            )
            
            cand_id = selected_cand.get("id")
            cache_key = f"reranking_analysis_{cand_id}"
            
            # Setup session state cache
            if cache_key not in st.session_state:
                st.session_state[cache_key] = None
                
            if st.button("⚡ Run Re-Ranking Fit Analysis", use_container_width=True):
                if not rerank_jd.strip():
                    st.warning("Please input the Job Description first.")
                else:
                    with st.spinner("Analyzing Job Description and executing deep evaluation comparison..."):
                        try:
                            # 1. Analyze Job Description first to get structured Job Profile
                            job_payload = {"job_description": rerank_jd}
                            job_resp = requests.post(f"{BACKEND_URL}/jobs/analyze", json=job_payload)
                            
                            if job_resp.status_code == 200:
                                job_profile = job_resp.json()
                                
                                # 2. Run deep re-ranking fit analysis
                                rerank_payload = {
                                    "candidate_id": cand_id,
                                    "job_profile": job_profile
                                }
                                rerank_resp = requests.post(f"{BACKEND_URL}/search/rerank", json=rerank_payload)
                                if rerank_resp.status_code == 200:
                                    st.session_state[cache_key] = rerank_resp.json()
                                else:
                                    st.error("Failed to run deep profile comparison. Check backend logs.")
                            else:
                                st.error("Failed to parse Job Description. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error connecting to backend services: {str(e)}")
                            
            if st.session_state[cache_key] is not None:
                rep = st.session_state[cache_key]
                
                # Fit Score and Recommendation Row
                score = rep.get("overall_score", 0)
                rec = rep.get("hiring_recommendation", "N/A")
                conf = rep.get("confidence", 0.0)
                
                score_color = "#10b981" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")
                rec_color = "#10b981" if "Hire" in rec and "No" not in rec else "#ef4444"
                
                st.markdown(
                    f"""
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div style="background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;">
                            <div style="font-size: 3rem; font-weight: 800; color: {score_color};">{score}%</div>
                            <div style="font-size: 1rem; font-weight: 600; margin-top: 5px;">Overall LLM Fit Score</div>
                            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 2px;">Evaluation Confidence: {conf:.2f}</div>
                        </div>
                        <div style="background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                            <div style="font-size: 1.8rem; font-weight: 700; color: {rec_color}; text-transform: uppercase;">{rec}</div>
                            <div style="font-size: 1rem; font-weight: 600; margin-top: 10px; color: #e2e8f0;">Hiring Recommendation</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Split Strengths and Weaknesses
                c_str, c_wk = st.columns(2)
                with c_str:
                    st.markdown("##### 👍 Evaluated Strengths")
                    strengths = rep.get("strengths") or []
                    if strengths:
                        for s in strengths:
                            st.markdown(f"- {s}")
                    else:
                        st.caption("None highlighted.")
                        
                with c_wk:
                    st.markdown("##### ⚠️ Evaluated Gaps / Risks")
                    weaknesses = rep.get("weaknesses") or []
                    if weaknesses:
                        for w in weaknesses:
                            st.markdown(f"- {w}")
                    else:
                        st.caption("None highlighted.")
                        
                st.write("")
                # Missing skills list
                st.markdown("##### 🛠️ Missing Requested Skills")
                missing = rep.get("missing_skills") or []
                if missing:
                    pills_html = "".join([f"<span class='skill-pill' style='background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3);'>{m}</span>" for m in missing])
                    st.markdown(pills_html, unsafe_allow_html=True)
                else:
                    st.success("Candidate matches all skills requested in the Job Profile!")
                    
                # Recruiter Explanation details
                render_recruiter_explanation(rep)

        with tab4:
            st.markdown("#### 📋 Custom Interview Planner & Guide")
            st.write("Generate a structured list of interview questions tailored to candidate qualifications, job description expectations, soft skills, and missing technical skills.")
            
            planner_jd = st.text_area(
                "Job Description for Interview Guide", 
                height=150, 
                placeholder="Paste the job description to generate the custom interview plan...",
                key="planner_jd"
            )
            
            cand_id = selected_cand.get("id")
            cache_key = f"interview_planner_{cand_id}"
            
            # Setup session state cache
            if cache_key not in st.session_state:
                st.session_state[cache_key] = None
                
            if st.button("⚡ Generate Interview Plan", use_container_width=True):
                if not planner_jd.strip():
                    st.warning("Please input the Job Description first.")
                else:
                    with st.spinner("Compiling custom question sets..."):
                        try:
                            # 1. Analyze Job Description first to get structured Job Profile
                            job_payload = {"job_description": planner_jd}
                            job_resp = requests.post(f"{BACKEND_URL}/jobs/analyze", json=job_payload)
                            
                            if job_resp.status_code == 200:
                                job_profile = job_resp.json()
                                
                                # 2. Run interview planner
                                planner_payload = {
                                    "candidate_id": cand_id,
                                    "job_profile": job_profile
                                }
                                planner_resp = requests.post(f"{BACKEND_URL}/search/interview-plan", json=planner_payload)
                                if planner_resp.status_code == 200:
                                    st.session_state[cache_key] = planner_resp.json()
                                else:
                                    st.error("Failed to generate interview plan. Check backend logs.")
                            else:
                                st.error("Failed to parse Job Description. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error connecting to backend services: {str(e)}")
                            
            if st.session_state[cache_key] is not None:
                plan = st.session_state[cache_key]
                
                # Expose questions in expandable styled sections
                with st.expander("📡 Technical Competency Questions", expanded=True):
                    tech_q = plan.get("technical_questions") or []
                    if tech_q:
                        for idx, q in enumerate(tech_q):
                            st.markdown(f"**Q{idx+1}:** {q}")
                    else:
                        st.caption("No custom technical questions generated.")
                        
                with st.expander("🛠️ Missing Skills / Gap Probing Questions", expanded=True):
                    gap_q = plan.get("missing_skills_questions") or []
                    if gap_q:
                        for idx, q in enumerate(gap_q):
                            st.markdown(f"**Q{idx+1}:** {q}")
                    else:
                        st.success("Candidate matches all skills! No gap-probing questions needed.")
                        
                with st.expander("🧠 Behavioral & Cultural Traits Questions", expanded=False):
                    behav_q = plan.get("behavioral_questions") or []
                    if behav_q:
                        for idx, q in enumerate(behav_q):
                            st.markdown(f"**Q{idx+1}:** {q}")
                    else:
                        st.caption("No custom behavioral questions generated.")
                        
                with st.expander("👔 Leadership & Ownership Questions", expanded=False):
                    lead_q = plan.get("leadership_questions") or []
                    if lead_q:
                        for idx, q in enumerate(lead_q):
                            st.markdown(f"**Q{idx+1}:** {q}")
                    else:
                        st.caption("No leadership questions generated.")
                        
                with st.expander("🔍 Strategic Follow-Up Probes", expanded=False):
                    follow_q = plan.get("follow_up_questions") or []
                    if follow_q:
                        for idx, q in enumerate(follow_q):
                            st.markdown(f"**Q{idx+1}:** {q}")
                    else:
                        st.caption("No follow-up probes generated.")

        with st.container():
            # Spacing between tabs
            pass

        with tab3:
            st.markdown("#### 🛠️ Technical Skill Gap Analysis")
            st.write("Cross-reference candidate skills against a Job Description to evaluate gaps, identify transferable skills, estimate ramp-up times, and assess hiring risk.")
            
            gap_jd = st.text_area(
                "Job Description for Skill Gap Analysis", 
                height=150, 
                placeholder="Paste the job description to run the skill gap analysis...",
                key="gap_jd"
            )
            
            cand_id = selected_cand.get("id")
            cache_key = f"skillgap_analysis_{cand_id}"
            
            # Setup session state cache
            if cache_key not in st.session_state:
                st.session_state[cache_key] = None
                
            if st.button("⚡ Generate Skill Gap Report", use_container_width=True):
                if not gap_jd.strip():
                    st.warning("Please input the Job Description first.")
                else:
                    with st.spinner("Analyzing skill gaps and learning curves..."):
                        try:
                            # 1. Analyze Job Description first to get structured Job Profile
                            job_payload = {"job_description": gap_jd}
                            job_resp = requests.post(f"{BACKEND_URL}/jobs/analyze", json=job_payload)
                            
                            if job_resp.status_code == 200:
                                job_profile = job_resp.json()
                                
                                # 2. Run skill gap analysis
                                gap_payload = {
                                    "candidate_id": cand_id,
                                    "job_profile": job_profile
                                }
                                gap_resp = requests.post(f"{BACKEND_URL}/search/skill-gap", json=gap_payload)
                                if gap_resp.status_code == 200:
                                    st.session_state[cache_key] = gap_resp.json()
                                else:
                                    st.error("Failed to run skill gap assessment. Check backend logs.")
                            else:
                                st.error("Failed to parse Job Description. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error connecting to backend services: {str(e)}")
                            
            if st.session_state[cache_key] is not None:
                rep = st.session_state[cache_key]
                
                # Visual Metrics Row
                ramp_up = rep.get("estimated_ramp_up", "N/A")
                difficulty = rep.get("learning_difficulty", "N/A")
                
                diff_color = "#10b981" if difficulty == "Low" else ("#f59e0b" if difficulty == "Medium" else "#ef4444")
                
                st.markdown(
                    f"""
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div style="background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;">
                            <div style="font-size: 2.2rem; font-weight: 700; color: #60a5fa;">{ramp_up}</div>
                            <div style="font-size: 1rem; font-weight: 600; margin-top: 5px; color: #94a3b8;">Estimated Ramp-Up Time</div>
                        </div>
                        <div style="background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); text-align: center;">
                            <div style="font-size: 2.2rem; font-weight: 700; color: {diff_color};">{difficulty}</div>
                            <div style="font-size: 1rem; font-weight: 600; margin-top: 5px; color: #94a3b8;">Learning Difficulty</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Hiring Risk Banner
                risk_text = rep.get("hiring_risk", "N/A")
                risk_bg = "rgba(239, 68, 68, 0.05)" if "High" in risk_text else ("rgba(245, 158, 11, 0.05)" if "Medium" in risk_text else "rgba(16, 185, 129, 0.05)")
                risk_border = "#ef4444" if "High" in risk_text else ("#f59e0b" if "Medium" in risk_text else "#10b981")
                risk_color = "#f87171" if "High" in risk_text else ("#fbbf24" if "Medium" in risk_text else "#34d399")
                
                st.markdown(
                    f"""
                    <div style="background: {risk_bg}; padding: 1.2rem; border-radius: 10px; border-left: 5px solid {risk_border}; margin-bottom: 20px;">
                        <strong style="color: {risk_color}; font-size: 1.05rem;">⚠️ Technical Hiring Risk Assessment</strong>
                        <p style="margin: 5px 0 0 0; line-height: 1.5; color: #e2e8f0;">{risk_text}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Split Gaps and Transferable skills
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown("##### 🚨 Missing Required Skills")
                    missing = rep.get("missing_skills") or []
                    if missing:
                        missing_pills = "".join([f"<span class='skill-pill' style='background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3);'>{m}</span>" for m in missing])
                        st.markdown(missing_pills, unsafe_allow_html=True)
                    else:
                        st.success("No missing skills! Candidate matches all requested requirements.")
                        
                with col_g2:
                    st.markdown("##### 🌉 Transferable Skills & Concept Bridges")
                    trans = rep.get("transferable_skills") or []
                    if trans:
                        for t in trans:
                            st.markdown(f"- {t}")
                    else:
                        st.caption("No conceptual bridges highlighted.")

        with tab5:
            st.markdown("#### Automated JD Fit Analysis")
            jd_input = st.text_area(
                "Compare against Job Description", 
                height=150, 
                placeholder="Paste the job description here to run the fit report...",
                key="screening_jd"
            )
            
            if st.button("⚡ Generate Report", use_container_width=True):
                if not jd_input.strip():
                    st.warning("Please input a Job Description first.")
                else:
                    with st.spinner("Screening resume against Job Description via GPT..."):
                        payload = {"job_description": jd_input}
                        try:
                            response = requests.post(f"{BACKEND_URL}/search/screen/{selected_cand.get('id')}", json=payload)
                            if response.status_code == 200:
                                report = response.json()
                                
                                # Render report beautifully
                                fit_score = report.get("fit_score", 0)
                                score_color = "#10b981" if fit_score >= 70 else ("#f59e0b" if fit_score >= 40 else "#ef4444")
                                
                                st.markdown(
                                    f"""
                                    <div style="display: flex; align-items: center; gap: 20px; background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.05);">
                                        <div style="font-size: 3rem; font-weight: 800; color: {score_color};">{fit_score}%</div>
                                        <div>
                                            <div style="font-size: 1.2rem; font-weight: 600;">Overall Job Suitability Score</div>
                                            <div style="color: #94a3b8; font-size: 0.95rem;">Based on skill match, experience alignment, and background evaluation.</div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                
                                st.markdown(f"**Match Summary:**\n{report.get('match_summary')}")
                                
                                col_pros, col_cons = st.columns(2)
                                with col_pros:
                                    st.markdown("##### 👍 Strengths / Pros")
                                    pros_list = "".join([f"<li>{item}</li>" for item in report.get("pros", [])])
                                    st.markdown(f'<ul class="pros-list">{pros_list}</ul>', unsafe_allow_html=True)
                                    
                                with col_cons:
                                    st.markdown("##### ⚠️ Gaps / Cons / Risks")
                                    cons_list = "".join([f"<li>{item}</li>" for item in report.get("cons", [])])
                                    st.markdown(f'<ul class="cons-list">{cons_list}</ul>', unsafe_allow_html=True)
                                    
                                st.write("")
                                st.markdown("##### ❓ Tailored Interview Questions")
                                q_list = "".join([f"<li>{item}</li>" for item in report.get("interview_questions", [])])
                                st.markdown(f'<ol class="q-list">{q_list}</ol>', unsafe_allow_html=True)
                                
                            else:
                                st.error("Failed to generate screening report. Check backend logs.")
                        except Exception as e:
                            st.error(f"Error connecting to backend screening service: {str(e)}")
                            
        with tab6:
            st.markdown(f"#### Ask questions about **{selected_cand.get('name')}**")
            
            # Setup session state for chat history
            state_key = f"chat_history_{selected_cand.get('id')}"
            if state_key not in st.session_state:
                st.session_state[state_key] = []
                
            # Display chat logs
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state[state_key]:
                    role_icon = "👤" if msg["role"] == "user" else "🤖"
                    bg_color = "rgba(59, 130, 246, 0.1)" if msg["role"] == "user" else "rgba(30, 41, 59, 0.4)"
                    align = "text-align: right;" if msg["role"] == "user" else "text-align: left;"
                    
                    st.markdown(
                        f"""
                        <div style="background: {bg_color}; padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem; border: 1px solid rgba(255, 255, 255, 0.05);">
                            <span style="font-size: 1.2rem; margin-right: 8px;">{role_icon}</span>
                            <strong>{'You' if msg['role'] == 'user' else 'AI Interviewer'}:</strong>
                            <p style="margin: 5px 0 0 0; white-space: pre-wrap;">{msg['content']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            
            # Query input
            user_msg = st.chat_input("Ask a question (e.g., 'What tech stack has this candidate used?')")
            if user_msg:
                # Append user query to chat history
                st.session_state[state_key].append({"role": "user", "content": user_msg})
                
                # Fetch history excluding system roles
                payload = {
                    "message": user_msg,
                    "history": st.session_state[state_key][:-1] # Send history up to current question
                }
                
                with st.spinner("AI is reading resume..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/search/chat/{selected_cand.get('id')}", json=payload)
                        if response.status_code == 200:
                            reply = response.json().get("reply", "")
                            st.session_state[state_key].append({"role": "assistant", "content": reply})
                            st.rerun()
                        else:
                            st.error("Failed to generate AI response.")
                    except Exception as e:
                        st.error(f"Error querying chat API: {str(e)}")
