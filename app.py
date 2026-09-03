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
# CẤU HÌNH TRANG & BIẾN MẶC ĐỊNH
# ==========================================
st.set_page_config(page_title="AIC 2026 Workspace", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

DB_FILE = "task_database.json"
SUBMISSION_LOG_FILE = "submission_log.json"
TEAM_MEMBERS = ["VThành", "LThiện", "PThiện", "Nguyên", "NThành"]
SUFFIX_MAP = {"Textual KIS": "kis", "Q&A": "qa", "TRAKE": "trake"}
MAX_ANSWER_LEN = 100

# ==========================================
# THEME — HỆ THỐNG DESIGN SYSTEM (UI UX PRO MAX)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root {
    --bg-main: #0B0F19;
    --bg-sidebar: #0D1322;
    --bg-card: #151C2C;
    --bg-card-hover: #1E293B;
    --border-color: #2A3441;
    
    --accent-cyan: #06B6D4;
    --accent-indigo: #6366F1;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    
    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    
    --font-sans: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

/* Base Styles */
html, body, [class^="css"], [class*=" css"] { font-family: var(--font-sans); color: var(--text-main); }
[data-testid="stAppViewContainer"] { background: var(--bg-main); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: var(--bg-sidebar); border-right: 1px solid var(--border-color); }
h1, h2, h3, h4 { font-weight: 700 !important; letter-spacing: -0.02em; }
p, span, div { color: var(--text-main); }
.stCaption, [data-testid="stCaptionContainer"] p { color: var(--text-muted) !important; font-size: 0.85rem !important; }

/* Typography Mono for Data */
code, .mono-text, .stTextInput input, .stTextArea textarea, .stNumberInput input {
    font-family: var(--font-mono) !important;
}

/* Cards & Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card);
    border: 1px solid var(--border-color) !important;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: rgba(11, 15, 25, 0.5) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2) !important;
}
div[role="radiogroup"] input { accent-color: var(--accent-cyan); }

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 8px; font-weight: 600; border: 1px solid var(--border-color);
    background: var(--bg-card); color: var(--text-main); transition: all 0.2s;
}
.stButton > button:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
    color: white !important; border: none; font-weight: 700;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.15); transform: translateY(-1px); }

/* Sidebar Navigation Buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100%; justify-content: flex-start; padding: 0.75rem 1rem;
    background: transparent; border: 1px solid transparent; text-align: left;
}
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.05); }

/* Progress Bar & Metrics */
[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo)); }
[data-testid="stMetricValue"] { font-family: var(--font-mono) !important; color: var(--accent-cyan) !important; }

/* Custom UI Elements */
.header-eyebrow { font-family: var(--font-mono); font-size: 11px; color: var(--accent-cyan); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }
.badge { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-mono); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 99px; }
.badge-done { background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-todo { background: rgba(244, 63, 94, 0.15); color: var(--danger); border: 1px solid rgba(244, 63, 94, 0.3); }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.badge-done .dot { background: var(--success); box-shadow: 0 0 6px var(--success); }
.badge-todo .dot { background: var(--danger); }
</style>
""", unsafe_allow_html=True)

def page_header(title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div class="header-eyebrow">AIC 2026 · TACTICAL COMMAND</div>
        <h2 style="margin: 0; font-size: 28px;">{title}</h2>
        <div style="color: var(--text-muted); margin-top: 4px;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def status_badge(status_str):
    is_done = "Hoàn thành" in status_str
    css = "badge-done" if is_done else "badge-todo"
    return f'<div class="badge {css}"><div class="dot"></div>{status_str}</div>'

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
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state: st.session_state.db = load_db()
db = st.session_state.db

if "current_member" not in st.session_state: st.session_state.current_member = None

def load_submission_log():
    if os.path.exists(SUBMISSION_LOG_FILE):
        try:
            with open(SUBMISSION_LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return []

def save_submission_log(log):
    with open(SUBMISSION_LOG_FILE, "w", encoding="utf-8") as f: json.dump(log, f, ensure_ascii=False, indent=2)

if "submission_log" not in st.session_state: st.session_state.submission_log = load_submission_log()

def validate_csv_content(content_str, task_type, num_events=None):
    rows = [row for row in csv.reader(io.StringIO(content_str)) if row]
    errors = []
    if len(rows) != 100: errors.append(f"❌ Sai số dòng: Đang có {len(rows)} dòng (Yêu cầu chính xác 100).")
    for idx, parts in enumerate(rows):
        if task_type == "Textual KIS" and len(parts) != 2:
            errors.append(f"❌ Dòng {idx+1}: KIS cần đúng 2 cột (video_id, frame_id).")
            break
        elif task_type == "Q&A":
            if len(parts) < 3: errors.append(f"❌ Dòng {idx+1}: Q&A cần 3 cột."); break
            elif len(parts[2]) > MAX_ANSWER_LEN: errors.append(f"❌ Dòng {idx+1}: Câu trả lời vượt quá {MAX_ANSWER_LEN} ký tự."); break
        elif task_type == "TRAKE":
            expected = (num_events + 1) if num_events else None
            if expected and len(parts) != expected: errors.append(f"❌ Dòng {idx+1}: TRAKE cần {expected} cột."); break
            elif not expected and len(parts) < 3: errors.append(f"❌ Dòng {idx+1}: TRAKE cần ít nhất 3 cột."); break
    return len(errors) == 0, errors

def generate_spam_csv(video_id, input_frames, is_qa, qa_answer, total_target=100, step=5):
    if not input_frames: return ""
    base_quota = total_target // len(input_frames)
    remainder = total_target % len(input_frames)
    quotas = [base_quota + (1 if i < remainder else 0) for i in range(len(input_frames))]
    
    seen, final_results = set(), []
    for i, base_frame in enumerate(input_frames):
        curr, offset = [], step
        if (video_id, base_frame) not in seen:
            seen.add((video_id, base_frame)); curr.append((video_id, base_frame))
        while len(curr) < quotas[i]:
            for df in [offset, -offset]:
                f_new = base_frame + df
                if f_new >= 0 and (video_id, f_new) not in seen and len(curr) < quotas[i]:
                    seen.add((video_id, f_new)); curr.append((video_id, f_new))
            offset += step
        final_results.extend(curr)
    lines = [build_csv_row([v, f, qa_answer] if is_qa else [v, f]) for v, f in final_results[:total_target]]
    return "\n".join(lines)

def generate_range_csv(video_id, start_frame, end_frame, is_qa, qa_answer, total_target=100):
    frames = []
    if total_target == 1: frames.append(start_frame)
    else:
        step = max(1, (end_frame - start_frame) / (total_target - 1))
        for i in range(total_target): frames.append(int(round(start_frame + i * step)))
    lines = [build_csv_row([video_id, f, qa_answer] if is_qa else [video_id, f]) for f in frames[:total_target]]
    return "\n".join(lines)

def generate_trake_csv(video_id, event_frames, total_target=100, step=5):
    if not event_frames: return ""
    seen, sequences = set(), []
    base_seq = tuple(event_frames)
    seen.add(base_seq); sequences.append(base_seq)
    offset = step
    while len(sequences) < total_target and offset < 100000:
        for delta in (offset, -offset):
            new_seq = tuple(f + delta for f in event_frames)
            if all(f >= 0 for f in new_seq) and new_seq not in seen and len(sequences) < total_target:
                seen.add(new_seq); sequences.append(new_seq)
        offset += step
    lines = [build_csv_row([video_id, *seq]) for seq in sequences[:total_target]]
    return "\n".join(lines)

def time_to_sec(t_str):
    try: h, m, s = map(int, t_str.split(':')); return h*3600 + m*60 + s
    except: return -1

def create_zip_file(db_data):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for q_id, info in db_data.items():
            if info.get("status") == "🟢 Hoàn thành" and info.get("csv_content"):
                zip_file.writestr(f"submission/{q_id}.csv", info["csv_content"])
    return zip_buffer.getvalue()

def auto_extract_data(raw_text):
    """Trích xuất tự động Video ID và list Frame từ Raw text để user khỏi gõ tay"""
    vids = re.findall(r'(L\d+_V\d+)', raw_text)
    frames = re.findall(r'(?:frame\s*=\s*|:|,|^|\s)(\d{3,6})(?:\s|$|,)', raw_text)
    vid = vids[0] if vids else ""
    return vid, ", ".join(frames[:10]) # Lấy top 10 frame

# ==========================================
# AUTH SCREEN (CHỌN THÀNH VIÊN)
# ==========================================
if st.session_state.current_member is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.markdown("<h1 style='color:var(--accent-cyan); font-size:48px;'>⚡</h1>", unsafe_allow_html=True)
            st.markdown("<h2 style='margin-bottom:0;'>AIC 2026 Workspace</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:var(--text-muted); margin-bottom:20px;'>Hệ thống quản lý truy vấn đa phương tiện</p>", unsafe_allow_html=True)
            selected_name = st.selectbox("Xác thực thành viên tác chiến:", TEAM_MEMBERS)
            if st.button("🚀 KHỞI ĐỘNG HỆ THỐNG", type="primary", use_container_width=True):
                st.session_state.current_member = selected_name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_member = st.session_state.current_member

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(f"<h3 style='color:var(--accent-cyan);'>⚡ AIC Workspace</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:var(--font-mono); font-size:13px; margin-bottom: 20px;'>User: <span style='color:var(--accent-cyan);'>{current_member}</span></div>", unsafe_allow_html=True)
    
    total_q = len(db)
    done_q = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
    prog = done_q / total_q if total_q > 0 else 0
    
    with st.container(border=True):
        st.markdown(f"**TIẾN ĐỘ ĐỘI ({int(prog*100)}%)**")
        st.progress(prog)
        st.markdown(f"<div style='text-align:right; font-family:var(--font-mono); color:var(--text-muted);'>{done_q} / {total_q} Queries</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    NAV_ITEMS = ["📋 Quản Lý Nhiệm Vụ", "⚙️ Auto-Generator (Spam)", "📤 Cập Nhật External CSV", "📦 Kiểm Tra & Đóng Gói"]
    if "menu" not in st.session_state: st.session_state.menu = NAV_ITEMS[0]
    
    for item in NAV_ITEMS:
        is_active = st.session_state.menu == item
        if st.button(item, key=f"nav_{item}", type="primary" if is_active else "secondary"):
            st.session_state.menu = item
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🛠️ Cài đặt hệ thống"):
        if st.button("🔄 Đổi tài khoản", use_container_width=True):
            st.session_state.current_member = None; st.rerun()
        if st.checkbox("Mở khóa Reset DB"):
            if st.button("🧹 Xóa sạch Database", use_container_width=True):
                st.session_state.db = {}; save_db({}); st.rerun()

menu = st.session_state.menu

# ==========================================
# MAIN ROUTER
# ==========================================

if menu == "📋 Quản Lý Nhiệm Vụ":
    page_header("Quản Lý & Phân Công Nhiệm Vụ", "Tạo các truy vấn (Queries) từ đề thi để cả đội cùng thấy và xử lý.")
    c1, c2 = st.columns([1, 1.5], gap="large")
    
    with c1:
        with st.container(border=True):
            st.markdown("#### ➕ Tạo Truy Vấn Mới")
            q_name = st.text_input("Tên Query (VD: query-p2-1-kis):")
            q_type = st.radio("Loại Task:", ["Textual KIS", "Q&A", "TRAKE"], horizontal=True)
            q_num = st.number_input("Số lượng sự kiện (Chỉ dùng cho TRAKE):", min_value=2, value=4) if q_type == "TRAKE" else None
            q_desc = st.text_area("Miêu tả ngữ cảnh video:", height=100)
            q_raw = st.text_area("Paste Top K Dữ Liệu Raw (Tùy chọn):", height=100)
            
            if st.button("Thêm Vào Hàng Đợi", type="primary", use_container_width=True):
                if not q_name: st.error("Tên Query không được để trống!")
                else:
                    db[q_name] = {
                        "type": q_type, "description": q_desc, "raw_data": q_raw,
                        "status": "🔴 Chưa làm", "assigned_to": current_member, "csv_content": "",
                        "num_events": int(q_num) if q_num else None
                    }
                    save_db(db); st.toast("Đã thêm thành công!", icon="✅"); st.rerun()

    with c2:
        st.markdown("#### 📑 Danh Sách Chờ Xử Lý")
        if not db: st.info("Chưa có truy vấn nào được khởi tạo.")
        for q_id, info in reversed(list(db.items())):
            with st.container(border=True):
                col_a, col_b = st.columns([0.8, 0.2])
                with col_a:
                    badge = status_badge(info['status'])
                    ty = f"TRAKE N={info['num_events']}" if info['type']=="TRAKE" else info['type']
                    st.markdown(f"{badge} &nbsp; <span style='font-size:18px; font-weight:700;'>{q_id}</span> &nbsp; <span style='color:var(--accent-cyan); font-family:var(--font-mono); font-size:12px;'>[{ty}]</span>", unsafe_allow_html=True)
                    st.caption(f"Trách nhiệm: {info.get('assigned_to', 'N/A')} | {info['description'][:80]}...")
                with col_b:
                    if st.button("🗑️ Xóa", key=f"del_{q_id}"):
                        del db[q_id]; save_db(db); st.rerun()

elif menu == "⚙️ Auto-Generator (Spam)":
    page_header("AI Generation Engine", "Cải tiến UX: Tạo file Spam chuẩn 100 dòng và TỰ ĐỘNG LƯU VÀO DATABASE chỉ với 1 click.")
    
    pending_qs = {k: v for k, v in db.items() if v["status"] == "🔴 Chưa làm"}
    if not pending_qs:
        st.success("Tất cả các Query đều đã hoàn thành hoặc chưa có Query nào!")
    else:
        selected_q = st.selectbox("🎯 Chọn Query đang làm:", list(pending_qs.keys()))
        info = db[selected_q]
        
        # UX Enhancement: Auto-Parse Raw Data
        pre_vid, pre_frames = "", ""
        if info['raw_data']:
            pre_vid, pre_frames = auto_extract_data(info['raw_data'])
            
        with st.container(border=True):
            st.markdown(f"**Thông tin Query:** `{selected_q}` | Loại: `{info['type']}` | Người tạo: `{info['assigned_to']}`")
            if info['raw_data']:
                with st.expander("Xem dữ liệu Raw"): st.code(info['raw_data'])
                
        t1, t2, t3 = st.tabs(["🎯 Tỏa Tròn (Point)", "⏱️ Khoảng (Range)", "🔗 Chuỗi (TRAKE)"])
        
        with t1:
            c1, c2 = st.columns([1, 1])
            with c1:
                vid1 = st.text_input("Video ID:", value=pre_vid, key="v1")
                f1 = st.text_area("Frames gốc (cách nhau dấu phẩy):", value=pre_frames, key="f1")
                ans1 = st.text_input("Answer (Chỉ cho Q&A):", key="a1") if info['type'] == "Q&A" else ""
            with c2:
                step1 = st.number_input("Bước nhảy (Step):", value=5, min_value=1, key="s1")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 TẠO FILE & LƯU VÀO HỆ THỐNG", type="primary", use_container_width=True, key="b1"):
                    frames_list = [int(x) for x in re.findall(r'\d+', f1)]
                    csv_str = generate_spam_csv(vid1, frames_list, info['type']=="Q&A", ans1, 100, step1)
                    if csv_str:
                        db[selected_q].update({"csv_content": csv_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                        save_db(db); st.success("Đã nén vào DB thành công!"); st.balloons(); st.rerun()

        with t2:
            c1, c2 = st.columns([1, 1])
            with c1:
                vid2 = st.text_input("Video ID:", value=pre_vid, key="v2")
                t_start = st.text_input("Bắt đầu (HH:MM:SS):", value="00:00:00", key="ts2")
                t_end = st.text_input("Kết thúc (HH:MM:SS):", value="00:01:00", key="te2")
                ans2 = st.text_input("Answer (Chỉ cho Q&A):", key="a2") if info['type'] == "Q&A" else ""
            with c2:
                fps = st.number_input("FPS:", value=25, key="fps2")
                st.markdown("<br><br><br>", unsafe_allow_html=True)
                if st.button("🚀 TẠO FILE & LƯU VÀO HỆ THỐNG", type="primary", use_container_width=True, key="b2"):
                    s_sec, e_sec = time_to_sec(t_start), time_to_sec(t_end)
                    if s_sec >= 0 and e_sec > s_sec:
                        csv_str = generate_range_csv(vid2, s_sec*fps, e_sec*fps, info['type']=="Q&A", ans2, 100)
                        db[selected_q].update({"csv_content": csv_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                        save_db(db); st.success("Đã nén vào DB thành công!"); st.balloons(); st.rerun()
                    else: st.error("Thời gian không hợp lệ!")

        with t3:
            st.info("Chế độ này áp dụng riêng cho loại bài TRAKE (chuỗi sự kiện).")
            c1, c2 = st.columns([1, 1])
            with c1:
                vid3 = st.text_input("Video ID:", value=pre_vid, key="v3")
                f3 = st.text_area(f"Nhập ĐÚNG {info.get('num_events', 'N')} frames theo thứ tự sự kiện:", value=pre_frames, key="f3")
            with c2:
                step3 = st.number_input("Bước dịch chuyển chuỗi:", value=5, min_value=1, key="s3")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 TẠO FILE & LƯU VÀO HỆ THỐNG", type="primary", use_container_width=True, key="b3"):
                    frames_list = [int(x) for x in re.findall(r'\d+', f3)]
                    if len(frames_list) != info.get('num_events', len(frames_list)):
                        st.error(f"Cần nhập đúng {info.get('num_events')} frame!")
                    else:
                        csv_str = generate_trake_csv(vid3, frames_list, 100, step3)
                        db[selected_q].update({"csv_content": csv_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                        save_db(db); st.success("Đã nén vào DB thành công!"); st.balloons(); st.rerun()

elif menu == "📤 Cập Nhật External CSV":
    page_header("Validation & Manual Upload", "Tải lên file CSV bạn tự code/tools ngoài. Hệ thống sẽ tự động Validate chuẩn 100 dòng.")
    target_q = st.selectbox("Chọn Query để upload:", list(db.keys()))
    if target_q:
        up_file = st.file_uploader("Kéo thả file .CSV vào đây:", type=['csv'])
        if up_file:
            content = up_file.getvalue().decode('utf-8').strip()
            is_valid, errs = validate_csv_content(content, db[target_q]['type'], db[target_q].get('num_events'))
            
            if is_valid:
                st.success("✅ File chuẩn 100 dòng theo luật BTC!")
                if st.button("Lưu & Đánh Dấu Hoàn Thành", type="primary"):
                    db[target_q].update({"csv_content": content, "status": "🟢 Hoàn thành", "completed_by": current_member})
                    save_db(db); st.rerun()
            else:
                st.error("❌ Phát hiện lỗi Format:")
                for e in errs: st.write(e)

elif menu == "📦 Kiểm Tra & Đóng Gói":
    page_header("Package & Submit", "Đóng gói toàn bộ các file đã hoàn thành thành 1 file ZIP đúng cấu trúc BTC.")
    
    done_qs = {k: v for k, v in db.items() if v["status"] == "🟢 Hoàn thành"}
    
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.markdown("#### 🗜️ Tải File ZIP Nộp Bài")
            if not done_qs:
                st.warning("Chưa có Query nào hoàn thành để nén ZIP.")
            else:
                zip_name = st.text_input("Tên file nén:", value="AIC_Submission_Team.zip")
                if not zip_name.endswith('.zip'): zip_name += '.zip'
                
                zip_data = create_zip_file(db)
                st.download_button(
                    label="📥 DOWNLOAD ZIP NOW",
                    data=zip_data, file_name=zip_name, mime="application/zip",
                    type="primary", use_container_width=True
                )
                st.caption("Cấu trúc ZIP tự động bọc thư mục `submission/` theo chuẩn BTC.")
                
        with st.container(border=True):
            st.markdown("#### 🧾 Lịch Sử Nộp Trên Cổng BTC")
            logs = st.session_state.submission_log
            count = len(logs)
            color = "var(--danger)" if count >= 3 else "var(--accent-cyan)"
            st.markdown(f"<h1 style='color:{color}; text-align:center;'>{count}/3 Lần Nộp</h1>", unsafe_allow_html=True)
            if st.button("➕ Ghi nhận 1 lần đã nộp", use_container_width=True, disabled=count>=3):
                logs.append({"time": datetime.now().strftime("%H:%M:%S"), "by": current_member})
                save_submission_log(logs); st.rerun()
            if st.button("🔄 Reset cho tập truy vấn mới", use_container_width=True):
                st.session_state.submission_log = []; save_submission_log([]); st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### 👁️ Review File Đã Xong")
            if not done_qs: st.info("Trống.")
            else:
                view_q = st.selectbox("Chọn file kiểm tra chéo:", list(done_qs.keys()))
                st.code(done_qs[view_q]['csv_content'], language="csv")

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div style='text-align:center; padding-top:40px; color:var(--text-muted); font-size:12px; font-family:var(--font-mono);'>
    AIC Workspace 2026 • UI/UX Optimized Edition
</div>
""", unsafe_allow_html=True)
