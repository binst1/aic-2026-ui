import os
import re
import csv
import json
import io
import zipfile
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# CẤU HÌNH TRANG
# ==========================================
st.set_page_config(
    page_title="AIC 2026 Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "task_database.json"
SUBMISSION_LOG_FILE = "submission_log.json"
TEAM_MEMBERS = ["VThành", "LThiện", "PThiện", "Nguyên", "NThành"]
SUFFIX_MAP = {"Textual KIS": "kis", "Q&A": "qa", "TRAKE": "trake"}
MAX_ANSWER_LEN = 100

# ==========================================
# SYSTEM DESIGN TOKENS & CUSTOM CSS (UI UX PRO MAX)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Be+Vietnam+Pro:wght@400;500;600&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root {
  --bg-dark: #090D16;
  --bg-sidebar: #0D1322;
  --bg-card: #111827;
  --bg-card-hover: #162032;
  --border-color: #1F2937;
  --border-focus: #374151;
  
  --primary-cyan: #06B6D4;
  --primary-indigo: #6366F1;
  --accent-glow: rgba(6, 182, 212, 0.15);
  
  --success: #10B981;
  --success-bg: rgba(16, 185, 129, 0.12);
  --warning: #F59E0B;
  --warning-bg: rgba(245, 158, 11, 0.12);
  --danger: #EF4444;
  --danger-bg: rgba(239, 68, 68, 0.12);
  
  --text-white: #F8FAFC;
  --text-muted: #94A3B8;
  --text-subtle: #64748B;
  
  --font-heading: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'Be Vietnam Pro', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* Global Reset & Styling */
html, body, [class^="css"], [class*=" css"] {
  font-family: var(--font-body);
}

[data-testid="stAppViewContainer"] {
  background: var(--bg-dark);
  color: var(--text-white);
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stSidebar"] {
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
}

/* Typography Hierarchy */
h1, h2, h3, h4 {
  font-family: var(--font-heading) !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  color: var(--text-white) !important;
}

p, span, label, div {
  color: var(--text-white);
}

.stCaption, [data-testid="stCaptionContainer"] {
  color: var(--text-muted) !important;
  font-size: 13px;
}

/* Surface Cards & Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 12px !important;
  padding: 16px !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: var(--border-focus) !important;
}

/* Form Inputs & Controls */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background: #0B1120 !important;
  color: var(--text-white) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  font-family: var(--font-mono) !important;
  font-size: 13.5px !important;
  transition: all 0.2s ease;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
  border-color: var(--primary-cyan) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

[data-baseweb="select"] > div {
  background: #0B1120 !important;
  border-color: var(--border-color) !important;
  border-radius: 8px !important;
}

/* Buttons Styling */
.stButton > button, .stDownloadButton > button {
  border-radius: 8px !important;
  border: 1px solid var(--border-color) !important;
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  color: var(--text-white) !important;
  background: var(--bg-card) !important;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
  padding: 8px 16px !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: var(--primary-cyan) !important;
  color: var(--primary-cyan) !important;
  transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--primary-cyan), var(--primary-indigo)) !important;
  color: #FFFFFF !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25) !important;
}

.stButton > button[kind="primary"]:hover {
  filter: brightness(1.15);
  box-shadow: 0 6px 16px rgba(6, 182, 212, 0.35) !important;
  color: #FFFFFF !important;
}

/* Sidebar Navigation Items */
[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start !important;
  text-align: left !important;
  padding: 10px 14px !important;
  font-size: 14px !important;
  border-radius: 8px !important;
  margin-bottom: 4px !important;
  width: 100% !important;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid transparent !important;
  color: var(--text-muted) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
  background: rgba(255, 255, 255, 0.04) !important;
  border-color: var(--border-color) !important;
  color: var(--text-white) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: rgba(6, 182, 212, 0.12) !important;
  border: 1px solid var(--primary-cyan) !important;
  color: var(--primary-cyan) !important;
  box-shadow: none !important;
}

/* Metric Display */
[data-testid="stMetric"] {
  background: #0B1120;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 14px;
}

[data-testid="stMetricValue"] {
  font-family: var(--font-mono) !important;
  font-weight: 700 !important;
  color: var(--primary-cyan) !important;
}

/* Status Badges & Pills */
.badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.badge-done {
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-todo {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.badge-done .status-dot { background: var(--success); box-shadow: 0 0 6px var(--success); }
.badge-todo .status-dot { background: var(--danger); box-shadow: 0 0 6px var(--danger); }

.tag-type {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 2px 8px;
  margin-left: 6px;
}

/* Header & Banner Decor */
.header-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--primary-cyan);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.header-rule {
  height: 2px;
  width: 64px;
  background: linear-gradient(90deg, var(--primary-cyan), var(--primary-indigo), transparent);
  border-radius: 2px;
  margin: 10px 0 20px 0;
}

/* Tabs Styling */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
}

[data-testid="stTabs"] button {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 13.5px;
  color: var(--text-muted);
  border-radius: 6px 6px 0 0;
  padding: 8px 16px;
}

[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--primary-cyan) !important;
  border-bottom: 2px solid var(--primary-cyan) !important;
  background: rgba(6, 182, 212, 0.05);
}

/* Radio Custom Accent */
div[role="radiogroup"] input {
  accent-color: var(--primary-cyan);
}
</style>
""", unsafe_allow_html=True)


def logo_svg(size=36):
    """Logo Tactical Keyframe Search dạng Vector SVG sắc nét."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="40" height="40" rx="10" fill="url(#paint0_linear)"/>
      <path d="M10 14V10a2 2 0 0 1 2-2h4" stroke="#06B6D4" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M30 14V10a2 2 0 0 0-2-2h-4" stroke="#06B6D4" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M10 26v4a2 2 0 0 0 2 2h4" stroke="#06B6D4" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M30 26v4a2 2 0 0 1-2 2h-4" stroke="#06B6D4" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M17 14.5L26 20L17 25.5V14.5Z" fill="url(#paint1_linear)"/>
      <defs>
        <linearGradient id="paint0_linear" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
          <stop stop-color="#0F172A"/>
          <stop stop-offset="1" stop-color="#1E293B"/>
        </linearGradient>
        <linearGradient id="paint1_linear" x1="17" y1="14.5" x2="26" y2="25.5" gradientUnits="userSpaceOnUse">
          <stop stop-color="#06B6D4"/>
          <stop stop-offset="1" stop-color="#6366F1"/>
        </linearGradient>
      </defs>
    </svg>
    """


def page_header(icon, title, subtitle):
    """Header tiêu chuẩn giao diện UI/UX Pro Max."""
    st.markdown(f"""
    <div style="margin-bottom: 8px;">
      <div class="header-eyebrow">AIC 2026 WORKSPACE · TACTICAL STUDIO</div>
      <h1 style="margin: 0; font-size: 26px; display: flex; align-items: center; gap: 10px;">
        <span>{icon}</span> <span>{title}</span>
      </h1>
      <div style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">{subtitle}</div>
      <div class="header-rule"></div>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status_str):
    """Pill trạng thái có hiệu ứng LED nhỏ."""
    is_done = "Hoàn thành" in status_str
    css_class = "badge-done" if is_done else "badge-todo"
    return f'<span class="badge-pill {css_class}"><span class="status-dot"></span>{status_str}</span>'


# ==========================================
# BACKEND LOGIC
# ==========================================
def clean_video_id(vid):
    return re.sub(r'\.\w{2,4}$', '', vid.strip()) if vid else vid


def build_csv_row(fields):
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=",", quoting=csv.QUOTE_MINIMAL, lineterminator="")
    writer.writerow(fields)
    return buf.getvalue()


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


if "db" not in st.session_state:
    st.session_state.db = load_db()
db = st.session_state.db

if "current_member" not in st.session_state:
    st.session_state.current_member = None


def load_submission_log():
    if os.path.exists(SUBMISSION_LOG_FILE):
        try:
            with open(SUBMISSION_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_submission_log(log):
    with open(SUBMISSION_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


if "submission_log" not in st.session_state:
    st.session_state.submission_log = load_submission_log()


def validate_csv_content(content_str, task_type, num_events=None):
    rows = [row for row in csv.reader(io.StringIO(content_str)) if row]
    errors = []
    if len(rows) != 100:
        errors.append(f"❌ Sai số dòng: Đang có {len(rows)} dòng (Yêu cầu chính xác: 100 dòng).")
    for idx, parts in enumerate(rows):
        if task_type == "Textual KIS" and len(parts) != 2:
            errors.append(f"❌ Dòng {idx+1} sai định dạng KIS (Cần 2 cột: video_id, frame_id).")
        elif task_type == "Q&A":
            if len(parts) < 3:
                errors.append(f"❌ Dòng {idx+1} sai định dạng Q&A (Cần video_id, frame_id, answer).")
            elif len(parts) == 3 and len(parts[2]) > MAX_ANSWER_LEN:
                errors.append(f"❌ Dòng {idx+1}: Câu trả lời dài {len(parts[2])} ký tự (Tối đa {MAX_ANSWER_LEN}).")
        elif task_type == "TRAKE":
            expected = (num_events + 1) if num_events else None
            if expected and len(parts) != expected:
                errors.append(f"❌ Dòng {idx+1} sai định dạng TRAKE (Cần {expected} cột: video + {num_events} frames).")
            elif not expected and len(parts) < 3:
                errors.append(f"❌ Dòng {idx+1} sai định dạng TRAKE (Cần ít nhất video + 2 frames).")
    return len(errors) == 0, errors


def generate_spam_csv(video_id, input_frames, is_qa, qa_answer, total_target=100, step=5):
    if not input_frames:
        return ""
    base_quota = total_target // len(input_frames)
    remainder = total_target % len(input_frames)
    quotas = [base_quota + (1 if i < remainder else 0) for i in range(len(input_frames))]

    seen, final_results = set(), []
    for i, base_frame in enumerate(input_frames):
        curr, offset = [], step
        if (video_id, base_frame) not in seen:
            seen.add((video_id, base_frame))
            curr.append((video_id, base_frame))
        while len(curr) < quotas[i]:
            for df in [offset, -offset]:
                f_new = base_frame + df
                if f_new >= 0 and (video_id, f_new) not in seen and len(curr) < quotas[i]:
                    seen.add((video_id, f_new))
                    curr.append((video_id, f_new))
            offset += step
        final_results.extend(curr)

    lines = [build_csv_row([v, f, qa_answer] if is_qa else [v, f]) for v, f in final_results[:total_target]]
    return "\n".join(lines)


def generate_range_csv(video_id, start_frame, end_frame, is_qa, qa_answer, total_target=100):
    frames = []
    if total_target == 1:
        frames.append(start_frame)
    else:
        step = max(1, (end_frame - start_frame) / (total_target - 1))
        for i in range(total_target):
            f = int(round(start_frame + i * step))
            frames.append(f)

    lines = [build_csv_row([video_id, f, qa_answer] if is_qa else [video_id, f]) for f in frames[:total_target]]
    return "\n".join(lines)


def generate_trake_csv(video_id, event_frames, total_target=100, step=5):
    if not event_frames:
        return ""
    seen, sequences = set(), []
    base_seq = tuple(event_frames)
    seen.add(base_seq)
    sequences.append(base_seq)
    offset = step
    while len(sequences) < total_target and offset < 100000:
        for delta in (offset, -offset):
            new_seq = tuple(f + delta for f in event_frames)
            if all(f >= 0 for f in new_seq) and new_seq not in seen and len(sequences) < total_target:
                seen.add(new_seq)
                sequences.append(new_seq)
        offset += step
    lines = [build_csv_row([video_id, *seq]) for seq in sequences[:total_target]]
    return "\n".join(lines)


def time_to_sec(t_str):
    try:
        h, m, s = map(int, t_str.split(':'))
        return h * 3600 + m * 60 + s
    except Exception:
        return -1


def create_zip_file(db_data):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for q_id, info in db_data.items():
            if info.get("status") == "🟢 Hoàn thành" and info.get("csv_content"):
                file_name = f"submission/{q_id}.csv"
                zip_file.writestr(file_name, info["csv_content"])
    return zip_buffer.getvalue()


# ==========================================
# MÀN HÌNH ĐỊNH DANH (LOGIN CARD)
# ==========================================
if st.session_state.current_member is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; padding: 12px 0 8px 0;">
                {logo_svg(48)}
                <div class="header-eyebrow" style="margin-top: 12px;">AIC 2026 · TACTICAL WORKSPACE</div>
                <h2 style="margin: 4px 0 0 0; font-size: 22px;">Chào mừng trở lại! 👋</h2>
                <div style="color: var(--text-muted); font-size: 13.5px; margin-top: 4px;">
                    Chọn thành viên trực ban để bắt đầu phiên làm việc
                </div>
            </div>
            """, unsafe_allow_html=True)

            selected_name = st.selectbox("👤 Thành viên:", TEAM_MEMBERS)

            if st.button("🚀 Bắt Đầu Phiên Làm Việc", type="primary", use_container_width=True):
                st.session_state.current_member = selected_name
                st.rerun()
    st.stop()

current_member = st.session_state.current_member

# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0 16px 0;">
        {logo_svg(38)}
        <div>
            <div style="font-family: var(--font-heading); font-weight: 700; font-size: 16px; line-height: 1.1;">
                AIC WORKSTATION
            </div>
            <div style="color: var(--text-muted); font-size: 11px; font-family: var(--font-mono); margin-top: 2px;">
                v2.0 · Pro Max Edition
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">ĐANG TRỰC BAN</div>
                <div style="font-weight: 700; font-size: 15px; color: var(--primary-cyan);">
                    👤 {current_member}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Đổi người", use_container_width=True):
            st.session_state.current_member = None
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Progression Tracker
    total_queries = len(db)
    completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
    prog = completed_queries / total_queries if total_queries > 0 else 0

    with st.container(border=True):
        st.markdown("**📊 Tiến Độ Gói Truy Vấn**")
        st.progress(prog)
        col_st1, col_st2 = st.columns(2)
        col_st1.metric("Đã xong", f"{completed_queries}/{total_queries}")
        col_st2.metric("Tỉ lệ", f"{int(prog * 100)}%")

    st.markdown("<div class='header-eyebrow' style='margin: 16px 0 6px 0;'>📍 ĐIỀU HƯỚNG TÁC CHIẾN</div>", unsafe_allow_html=True)

    NAV_ITEMS = [
        "📋 Quản Lý Query",
        "📤 Upload Nộp Bài",
        "🛠️ Tool Spam Nhanh",
        "📦 Tổng Hợp & Xuất File",
    ]
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = NAV_ITEMS[0]

    for item in NAV_ITEMS:
        is_active = st.session_state.selected_menu == item
        if st.button(item, key=f"nav_{item}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.selected_menu = item
            st.rerun()

    selected_menu = st.session_state.selected_menu

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.expander("⚙️ Cài đặt hệ thống"):
        confirm_clear = st.checkbox("Xác nhận xóa sạch DB", key="chk_del")
        if st.button("🧹 Reset Dữ Liệu Ngày Mới", disabled=not confirm_clear, use_container_width=True):
            st.session_state.db = {}
            save_db({})
            st.rerun()

# ==========================================
# MAIN WORKSPACE STAGE
# ==========================================

# --- PAGE 1: QUẢN LÝ QUERY ---
if selected_menu == "📋 Quản Lý Query":
    page_header("📋", "Quản Lý & Khởi Tạo Query", "Tạo nhiệm vụ truy vấn mới và phân công tiến độ cho các thành viên.")

    col_form, col_list = st.columns([1.2, 1.8], gap="large")

    with col_form:
        with st.container(border=True):
            st.subheader("➕ Thêm Query Mới")
            q_name = st.text_input("Tên Query:", placeholder="VD: query-p2-14-kis")
            q_type = st.radio("Loại bài:", ["Textual KIS", "Q&A", "TRAKE"], horizontal=True)

            expected_suffix = SUFFIX_MAP[q_type]
            if q_name and not q_name.lower().endswith(f"-{expected_suffix}"):
                st.warning(f"⚠️ Khuyên dùng đuôi \"-{expected_suffix}\" cho loại bài {q_type} (VD: {q_name}-{expected_suffix}).")

            q_num_events = None
            if q_type == "TRAKE":
                q_num_events = st.number_input("Số lượng events (N) trong chuỗi:", min_value=2, max_value=20, value=4)

            q_desc = st.text_area("Miêu tả nội dung video / gợi ý:", placeholder="VD: VĐV mặc áo xanh đua xe qua khúc cua...")
            q_raw_data = st.text_area("Dữ liệu truy vấn thô (Top-K Result):", height=120)

            if st.button("🚀 Khởi Tạo Query", type="primary", use_container_width=True):
                if q_name:
                    db[q_name] = {
                        "type": q_type,
                        "description": q_desc,
                        "raw_data": q_raw_data,
                        "status": "🔴 Chưa làm",
                        "assigned_to": current_member,
                        "csv_content": "",
                        "num_events": int(q_num_events) if q_num_events else None,
                    }
                    save_db(db)
                    st.toast(f"Đã khởi tạo query {q_name} thành công!", icon="✅")
                    st.rerun()
                else:
                    st.error("Vui lòng điền Tên Query!")

    with col_list:
        st.subheader("📑 Danh Sách Nhiệm Vụ Đang Mở")
        if not db:
            st.info("Chưa có query nào được tạo. Hãy khởi tạo ở bảng bên trái!")
        else:
            for q_id, info in list(db.items()):
                with st.container(border=True):
                    c1, c2 = st.columns([0.82, 0.18])
                    type_label = info['type']
                    if info['type'] == "TRAKE" and info.get("num_events"):
                        type_label = f"TRAKE · N={info['num_events']}"

                    c1.markdown(
                        f"{status_badge(info['status'])} &nbsp; <span style='font-family: var(--font-mono); font-weight:700; font-size:15px;'>`{q_id}`</span> <span class='tag-type'>{type_label}</span>",
                        unsafe_allow_html=True
                    )
                    c1.caption(f"📖 {info['description']}  |  *(Tạo bởi: {info.get('assigned_to', 'Ẩn danh')})*")

                    with c2:
                        if st.button("🗑️", key=f"d_{q_id}", help="Xóa query"):
                            del db[q_id]
                            save_db(db)
                            st.rerun()
                        if info['status'] == "🟢 Hoàn thành" and st.button("🔄", key=f"r_{q_id}", help="Đặt lại thành chưa xong"):
                            db[q_id]["status"] = "🔴 Chưa làm"
                            save_db(db)
                            st.rerun()

# --- PAGE 2: UPLOAD NỘP BÀI ---
elif selected_menu == "📤 Upload Nộp Bài":
    page_header("📤", "Upload & Validation CSV", "Kiểm tra cú pháp file CSV nộp bài trước khi đưa vào hàng chờ đóng gói.")

    if not db:
        st.info("Chưa có query nào trong hệ thống. Hãy tạo query ở mục Quản Lý Query trước.")
    else:
        col_up1, col_up2 = st.columns([1.2, 1])

        with col_up1:
            with st.container(border=True):
                target_q = st.selectbox("🎯 Chọn Query cần cập nhật:", list(db.keys()))
                up_file = st.file_uploader("Kéo thả file .CSV nộp bài vào đây:", type=['csv'])

                if up_file and target_q:
                    file_str = up_file.getvalue().decode("utf-8").strip()
                    is_valid, errs = validate_csv_content(file_str, db[target_q]["type"], db[target_q].get("num_events"))

                    if is_valid:
                        st.success("✅ File CSV hợp lệ chuẩn 100 dòng theo yêu cầu BTC!")
                        if st.button("💾 Cập Nhật Tiến Độ Hoàn Thành", type="primary", use_container_width=True):
                            db[target_q].update({
                                "csv_content": file_str,
                                "status": "🟢 Hoàn thành",
                                "completed_by": current_member
                            })
                            save_db(db)
                            st.balloons()
                            st.rerun()
                    else:
                        st.markdown("**Các lỗi phát hiện:**")
                        for e in errs:
                            st.error(e)

        with col_up2:
            if target_q:
                q_info = db[target_q]
                with st.container(border=True):
                    st.markdown(f"**Yêu cầu cho `{target_q}`:**")
                    st.markdown(f"- **Loại bài:** `{q_info['type']}`")
                    if q_info.get("num_events"):
                        st.markdown(f"- **Số lượng Events:** `{q_info['num_events']}`")
                    st.markdown(f"- **Mô tả:** {q_info['description']}")

# --- PAGE 3: TOOL SPAM NHANH ---
elif selected_menu == "🛠️ Tool Spam Nhanh":
    page_header("🛠️", "Tool Spam Keyframe Tự Do", "Sinh file CSV test 100 dòng tự động từ các mốc frame hoặc khoảng thời gian.")

    tab_point, tab_range, tab_trake = st.tabs([
        "🎯 Spam Tỏa Tròn (Point Expand)",
        "⏱️ Spam Khoảng Thời Gian (Time Range)",
        "🔗 Spam Chuỗi Sự Kiện (TRAKE)"
    ])

    # Tab 1: Point Expand
    with tab_point:
        col_inp, col_cfg = st.columns([1.1, 0.9])
        with col_inp:
            with st.container(border=True):
                s1_vid = clean_video_id(st.text_input("Video ID (VD: L21_V013):", key="s1_vid"))
                s1_frames = st.text_area("Các Frame ID mốc gốc (cách nhau bằng dấu phẩy):", key="s1_frames", placeholder="120, 450, 980")
                s1_type = st.radio("Loại bài:", ["Textual KIS", "Q&A"], horizontal=True, key="s1_type")
                s1_qa = ""
                if s1_type == "Q&A":
                    s1_qa = st.text_input("Câu trả lời Q&A (Answer):", key="s1_qa")
                    qa_len = len(s1_qa)
                    qa_color = "var(--danger)" if qa_len > MAX_ANSWER_LEN else ("var(--warning)" if qa_len > 85 else "var(--text-muted)")
                    st.markdown(
                        f"<div style='font-family:var(--font-mono); font-size:12px; color:{qa_color}; margin-top:-6px; text-align:right;'>Độ dài: {qa_len}/{MAX_ANSWER_LEN} ký tự</div>",
                        unsafe_allow_html=True
                    )

        with col_cfg:
            with st.container(border=True):
                s1_total = st.number_input("Tổng số dòng mong muốn:", min_value=1, max_value=500, value=100)
                s1_step = st.number_input("Bước nhảy tỏa tròn (Step Frame):", min_value=1, max_value=50, value=5)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("🚀 Sinh CSV (Tỏa Tròn)", type="primary", use_container_width=True):
                    parsed_f = [int(x) for x in re.findall(r'\d+', s1_frames)]
                    if not s1_vid or not parsed_f:
                        st.error("Vui lòng điền đủ Video ID và ít nhất 1 Frame mốc.")
                    else:
                        csv_out = generate_spam_csv(s1_vid, parsed_f, s1_type == "Q&A", s1_qa, s1_total, s1_step)
                        st.success(f"Đã khởi tạo thành công {s1_total} dòng!")
                        st.download_button("📥 Tải Tệp CSV Về Máy", data=csv_out, file_name=f"spam_point_{s1_vid}.csv", mime="text/csv", use_container_width=True)

    # Tab 2: Time Range
    with tab_range:
        col_inp2, col_cfg2 = st.columns([1.1, 0.9])
        with col_inp2:
            with st.container(border=True):
                s2_vid = clean_video_id(st.text_input("Video ID (VD: L21_V013):", key="s2_vid"))
                col_t1, col_t2 = st.columns(2)
                s2_start = col_t1.text_input("Thời gian đầu (HH:MM:SS):", placeholder="00:05:00")
                s2_end = col_t2.text_input("Thời gian cuối (HH:MM:SS):", placeholder="00:05:15")

                s2_type = st.radio("Loại bài:", ["Textual KIS", "Q&A"], horizontal=True, key="s2_type")
                s2_qa = ""
                if s2_type == "Q&A":
                    s2_qa = st.text_input("Câu trả lời Q&A (Answer):", key="s2_qa")
                    qa_len2 = len(s2_qa)
                    qa_color2 = "var(--danger)" if qa_len2 > MAX_ANSWER_LEN else ("var(--warning)" if qa_len2 > 85 else "var(--text-muted)")
                    st.markdown(
                        f"<div style='font-family:var(--font-mono); font-size:12px; color:{qa_color2}; margin-top:-6px; text-align:right;'>Độ dài: {qa_len2}/{MAX_ANSWER_LEN} ký tự</div>",
                        unsafe_allow_html=True
                    )

        with col_cfg2:
            with st.container(border=True):
                s2_fps = st.number_input("Tốc độ khung hình (FPS - Mặc định 25):", min_value=1, max_value=60, value=25)
                s2_total = st.number_input("Tổng số dòng (Phân bổ đều):", min_value=1, max_value=500, value=100)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("🚀 Sinh CSV (Rải Thảm Khoảng Thời Gian)", type="primary", use_container_width=True):
                    sec_start, sec_end = time_to_sec(s2_start), time_to_sec(s2_end)
                    if not s2_vid:
                        st.error("Thiếu Video ID!")
                    elif sec_start < 0 or sec_end < 0:
                        st.error("Thời gian nhập sai định dạng HH:MM:SS.")
                    elif sec_start >= sec_end:
                        st.error("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc!")
                    else:
                        frame_start, frame_end = sec_start * s2_fps, sec_end * s2_fps
                        csv_out2 = generate_range_csv(s2_vid, frame_start, frame_end, s2_type == "Q&A", s2_qa, s2_total)
                        st.success(f"Đã tạo thành công {s2_total} dòng!")
                        st.download_button("📥 Tải Tệp CSV Về Máy", data=csv_out2, file_name=f"spam_range_{s2_vid}.csv", mime="text/csv", use_container_width=True)

    # Tab 3: TRAKE Sequence
    with tab_trake:
        col_inp3, col_cfg3 = st.columns([1.1, 0.9])
        with col_inp3:
            with st.container(border=True):
                s3_vid = clean_video_id(st.text_input("Video ID (VD: L10_V001):", key="s3_vid"))
                s3_frames = st.text_area(
                    "Chuỗi Frame ID các event (theo thứ tự thời gian, cách nhau dấu phẩy):",
                    key="s3_frames",
                    placeholder="1200, 1850, 2100, 2450"
                )
                st.caption("💡 Thuật toán sẽ tịnh tiến cả chuỗi event đồng thời để giữ nguyên khoảng cách tương đối.")

        with col_cfg3:
            with st.container(border=True):
                s3_total = st.number_input("Tổng số dòng biến thể:", min_value=1, max_value=500, value=100, key="s3_total")
                s3_step = st.number_input("Bước dịch chuỗi (Step Frame):", min_value=1, max_value=50, value=5, key="s3_step")

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("🚀 Sinh CSV Chuỗi TRAKE", type="primary", use_container_width=True, key="s3_btn"):
                    parsed_events = [int(x) for x in re.findall(r'\d+', s3_frames)]
                    if not s3_vid or len(parsed_events) < 2:
                        st.error("Cần nhập Video ID và ít nhất 2 Frame ID sự kiện.")
                    else:
                        csv_out3 = generate_trake_csv(s3_vid, parsed_events, s3_total, s3_step)
                        st.success(f"Đã tạo thành công {s3_total} dòng chuỗi sự kiện!")
                        st.download_button("📥 Tải Tệp CSV Về Máy", data=csv_out3, file_name=f"spam_trake_{s3_vid}.csv", mime="text/csv", use_container_width=True)

# --- PAGE 4: TỔNG HỢP & XUẤT FILE ---
elif selected_menu == "📦 Tổng Hợp & Xuất File":
    page_header("📦", "Đóng Gói & Theo Dõi Nộp Bài", "Xem xét trạng thái tất cả các bài giải, nén file ZIP submission và ghi log nộp bài.")

    completed_queries = {k: v for k, v in db.items() if v["status"] == "🟢 Hoàn thành"}
    missing_queries = {k: v for k, v in db.items() if v["status"] == "🔴 Chưa làm"}

    tab_kiemtra, tab_donggoi, tab_theodoi = st.tabs([
        "👁️ Soát Lỗi File CSV",
        "🗜️ Đóng Gói File ZIP",
        "🧾 Theo Dõi Số Lần Nộp"
    ])

    with tab_kiemtra:
        col_xanh, col_do = st.columns([1.1, 0.9])

        with col_xanh:
            st.subheader(f"✅ Đã Hoàn Thành ({len(completed_queries)} file)")
            with st.container(border=True):
                if not completed_queries:
                    st.info("Chưa có query nào hoàn thành.")
                else:
                    target_view = st.selectbox("Xem chi tiết nội dung CSV:", list(completed_queries.keys()))
                    if target_view:
                        st.caption(f"Hoàn thành bởi: **{completed_queries[target_view].get('completed_by', 'Ẩn danh')}**")
                        st.code(completed_queries[target_view]["csv_content"], language="csv")

        with col_do:
            st.subheader(f"⚠️ Chưa Hoàn Thành ({len(missing_queries)} file)")
            with st.container(border=True):
                if not missing_queries:
                    st.success("Tất cả các query đã được hoàn thành!")
                    st.balloons()
                else:
                    for k in missing_queries.keys():
                        st.markdown(f"🔴 <span style='font-family:var(--font-mono);'>`{k}`</span>", unsafe_allow_html=True)

    with tab_donggoi:
        st.subheader("🗜️ Đóng gói thư mục submission/")
        st.caption("File ZIP tạo ra sẽ tự động bao gồm cấu trúc thư mục `submission/<query-id>.csv` chuẩn BTC.")

        if not completed_queries:
            st.warning("⚠️ Chưa có file nào hoàn thành để đóng gói.")
        else:
            col_zip1, col_zip2 = st.columns([1, 1])
            with col_zip1:
                with st.container(border=True):
                    zip_filename = st.text_input("Tên file ZIP xuất ra:", value="submit_lan_1.zip")
                    if not zip_filename.endswith(".zip"):
                        zip_filename += ".zip"

                    if st.button("📦 Nén ZIP Ngay", type="primary", use_container_width=True):
                        zip_data = create_zip_file(db)
                        st.success(f"Đã đóng gói thành công {len(completed_queries)} file!")
                        st.download_button(
                            label=f"📥 CLICK TẢI {zip_filename}",
                            data=zip_data,
                            file_name=zip_filename,
                            mime="application/zip",
                            use_container_width=True
                        )

            with col_zip2:
                with st.container(border=True):
                    st.markdown("**Cấu trúc danh sách trong ZIP:**")
                    for k in completed_queries.keys():
                        st.markdown(f"📄 `submission/{k}.csv`")

    with tab_theodoi:
        st.subheader("🧾 Nhật Ký Giới Hạn Nộp Bài (Max 3 lần)")
        st.caption("Quy định BTC: Tối đa 3 lần nộp cho mỗi gói truy vấn. Đánh dấu ngay khi bấm nộp trên portal.")

        log = st.session_state.submission_log
        count = len(log)
        bar_color = "var(--danger)" if count >= 3 else ("var(--warning)" if count == 2 else "var(--success)")

        with st.container(border=True):
            st.markdown(
                f"<div style='font-family:var(--font-mono); font-size:46px; font-weight:700; color:{bar_color};'>{count} / 3</div>",
                unsafe_allow_html=True
            )

            if count >= 3:
                st.error("⚠️ Đã hết lượt nộp cho gói hiện tại! Kết quả tính điểm sẽ lấy theo lần nộp thứ 3.")
            elif count == 2:
                st.warning("⚠️ Chỉ còn 1 lượt nộp cuối cùng — hãy soát lại toàn bộ file trước khi gửi.")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                if st.button("➕ Đánh Dấu Đã Nộp Lần Này", type="primary", use_container_width=True, disabled=count >= 3):
                    st.session_state.submission_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "member": current_member,
                    })
                    save_submission_log(st.session_state.submission_log)
                    st.rerun()

            with col_sub2:
                confirm_reset_sub = st.checkbox("Xác nhận reset gói")
                if st.button("🔄 Reset Nhật Ký (Cho Gói Mới)", use_container_width=True, disabled=not confirm_reset_sub):
                    st.session_state.submission_log = []
                    save_submission_log([])
                    st.rerun()

        if log:
            st.markdown("**Lịch sử các lần đánh dấu:**")
            for idx, entry in reversed(list(enumerate(log, start=1))):
                st.markdown(f"- **Lần {idx}:** {entry['time']} — *Thực hiện bởi: {entry['member']}*")
