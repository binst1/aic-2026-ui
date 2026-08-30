import os
import re
import json
import io
import zipfile
import pandas as pd
import streamlit as st

# ==========================================
# CẤU HÌNH TRANG & BIẾN MẶC ĐỊNH
# ==========================================
st.set_page_config(page_title="AIC 2026 Workspace", page_icon="🎞️", layout="wide", initial_sidebar_state="expanded")

DB_FILE = "task_database.json"
TEAM_MEMBERS = ["VThành", "LThiện", "PThiện", "Nguyên", "NThành"]

# ==========================================
# THEME — token hệ thống + CSS
# ==========================================
# Bảng màu lấy cảm hứng từ phòng dựng video: nền graphite tối, điểm nhấn
# teal như vệt waveform/timeline, dữ liệu frame/timecode dùng font mono.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Be+Vietnam+Pro:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

:root{
  --bg-primary:#0B0F1A;
  --bg-secondary:#0F1524;
  --bg-surface:#161D2E;
  --border-subtle:#232C42;
  --accent:#2DD4BF;
  --accent-strong:#14B8A6;
  --accent-soft:rgba(45,212,191,0.12);
  --warning:#F59E0B;
  --danger:#F87171;
  --success:#34D399;
  --text-primary:#F1F5F9;
  --text-muted:#94A3B8;
  --font-display:'Sora',sans-serif;
  --font-body:'Be Vietnam Pro',sans-serif;
  --font-mono:'JetBrains Mono',monospace;
}

html, body, [class^="css"], [class*=" css"]{ font-family:var(--font-body); }
[data-testid="stAppViewContainer"]{ background:var(--bg-primary); }
[data-testid="stHeader"]{ background:transparent; }
[data-testid="stSidebar"]{ background:var(--bg-secondary); border-right:1px solid var(--border-subtle); }
[data-testid="stSidebar"] *{ color:var(--text-primary); }

h1,h2,h3{ font-family:var(--font-display) !important; font-weight:700 !important; letter-spacing:-0.01em; color:var(--text-primary); }
p, span, label, div{ color:var(--text-primary); }
.stCaption, [data-testid="stCaptionContainer"]{ color:var(--text-muted) !important; }

/* Thẻ viền (container border=True) */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--bg-surface);
  border:1px solid var(--border-subtle) !important;
  border-radius:14px;
}

/* Nút bấm */
.stButton > button, .stDownloadButton > button{
  border-radius:10px;
  border:1px solid var(--border-subtle);
  font-family:var(--font-body);
  font-weight:600;
  color:var(--text-primary);
  background:var(--bg-surface);
  transition:all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  border-color:var(--accent);
  color:var(--accent);
}
.stButton > button[kind="primary"]{
  background:linear-gradient(135deg,var(--accent-strong),var(--accent));
  color:#06201C;
  border:none;
}
.stButton > button[kind="primary"]:hover{
  filter:brightness(1.08);
  color:#06201C;
}

/* Thanh tiến độ */
[data-testid="stProgress"] div[role="progressbar"] > div{
  background:linear-gradient(90deg,var(--accent-strong),var(--accent)) !important;
  border-radius:6px;
}
[data-testid="stProgress"] div[role="progressbar"]{
  background:var(--bg-surface) !important;
  border-radius:6px;
}

/* Metric */
[data-testid="stMetric"]{
  background:var(--bg-surface);
  border:1px solid var(--border-subtle);
  border-radius:10px;
  padding:10px 14px;
}
[data-testid="stMetricValue"]{ font-family:var(--font-mono) !important; color:var(--accent) !important; }
[data-testid="stMetricLabel"]{ color:var(--text-muted) !important; }

/* Điều hướng sidebar (radio -> pill nav) */
[data-testid="stSidebar"] div[role="radiogroup"]{ gap:2px; }
[data-testid="stSidebar"] div[role="radiogroup"] label{
  border-radius:10px;
  padding:8px 10px;
  width:100%;
  font-weight:600;
  transition:background .15s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{ background:var(--accent-soft); }
[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"]{
  background:var(--accent-soft);
  border:1px solid var(--accent);
}
[data-testid="stSidebar"] div[role="radiogroup"] input{ accent-color:var(--accent); }

/* Input & selectbox */
.stTextInput input, .stTextArea textarea, .stNumberInput input{
  background:var(--bg-surface) !important;
  color:var(--text-primary) !important;
  border:1px solid var(--border-subtle) !important;
  border-radius:8px !important;
  font-family:var(--font-mono);
}
[data-baseweb="select"] > div{
  background:var(--bg-surface) !important;
  border-color:var(--border-subtle) !important;
  border-radius:8px !important;
}

/* Tabs */
[data-testid="stTabs"] button{ font-weight:600; }
[data-testid="stTabs"] [aria-selected="true"]{ color:var(--accent) !important; }

/* Badge trạng thái + logo */
.badge{
  font-family:var(--font-mono); font-size:12px; font-weight:600;
  padding:3px 10px; border-radius:999px; display:inline-block; letter-spacing:.02em;
}
.badge-done{ background:rgba(52,211,153,.15); color:var(--success); border:1px solid rgba(52,211,153,.35); }
.badge-todo{ background:rgba(248,113,113,.15); color:var(--danger); border:1px solid rgba(248,113,113,.35); }
.tag-type{
  font-family:var(--font-mono); font-size:11px; color:var(--text-muted);
  border:1px solid var(--border-subtle); border-radius:6px; padding:1px 6px; margin-left:6px;
}
.header-eyebrow{
  font-family:var(--font-mono); font-size:12px; color:var(--accent);
  letter-spacing:.08em; text-transform:uppercase; margin-bottom:2px;
}
.header-rule{ height:2px; width:56px; background:linear-gradient(90deg,var(--accent),transparent); border-radius:2px; margin:8px 0 18px 0; }
</style>
""", unsafe_allow_html=True)


def logo_svg(size=40):
    """Logo tự thiết kế: khung ngắm keyframe với dấu play — không phụ thuộc ảnh ngoài."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 12V6a2 2 0 0 1 2-2h6" stroke="#2DD4BF" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M36 12V6a2 2 0 0 0-2-2h-6" stroke="#2DD4BF" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M4 28v6a2 2 0 0 0 2 2h6" stroke="#2DD4BF" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M36 28v6a2 2 0 0 1-2 2h-6" stroke="#2DD4BF" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M16 13l11 7-11 7V13z" fill="#2DD4BF"/>
    </svg>
    """


def page_header(icon, title, subtitle):
    st.markdown(f"""
    <div class="header-eyebrow">AIC 2026 WORKSPACE</div>
    <h1 style="margin-bottom:0;">{icon} {title}</h1>
    <div style="color:var(--text-muted); margin-top:4px;">{subtitle}</div>
    <div class="header-rule"></div>
    """, unsafe_allow_html=True)


def status_badge(status_str):
    is_done = "Hoàn thành" in status_str
    css_class = "badge-done" if is_done else "badge-todo"
    return f'<span class="badge {css_class}">{status_str}</span>'


# ==========================================
# HÀM XỬ LÝ DỮ LIỆU (Backend) — giữ nguyên logic gốc
# ==========================================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: pass
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state: st.session_state.db = load_db()
db = st.session_state.db

if "current_member" not in st.session_state: st.session_state.current_member = None

def parse_raw_data(raw_data):
    results = []
    lines = raw_data.strip().split('\n')
    current_vid = None
    for line in lines:
        vid_match = re.search(r'(L\d+_V\d+)', line)
        if vid_match and 'keyframe' not in line: current_vid = vid_match.group(1)
        time_match = re.search(r'frame=(\d+)\s+time=(\d{2}:\d{2}:\d{2})', line)
        if time_match and current_vid:
            frame, time_str = time_match.group(1), time_match.group(2)
            h, m, s = map(int, time_str.split(':'))
            results.append({"video_id": current_vid, "frame": frame, "time_str": time_str, "seconds": h*3600 + m*60 + s})
            current_vid = None 
    return results

def validate_csv_content(content_str, task_type, num_events=None):
    raw_lines = [line.strip("\r") for line in content_str.split("\n") if line.strip("\r")]
    errors = []
    if len(raw_lines) != 100: errors.append(f"❌ Sai số dòng: Đang có {len(raw_lines)} dòng (Yêu cầu: 100).")
    for idx, line in enumerate(raw_lines):
        parts = line.split(",")
        if task_type == "Textual KIS" and len(parts) != 2: errors.append(f"❌ Dòng {idx+1} sai định dạng KIS.")
        elif task_type == "Q&A" and len(parts) < 3: errors.append(f"❌ Dòng {idx+1} sai định dạng Q&A.")
        elif task_type == "TRAKE":
            expected = (num_events + 1) if num_events else None
            if expected and len(parts) != expected:
                errors.append(f"❌ Dòng {idx+1} sai định dạng TRAKE (cần {expected} cột: video + {num_events} frame, đang có {len(parts)}).")
            elif not expected and len(parts) < 3:
                errors.append(f"❌ Dòng {idx+1} sai định dạng TRAKE (cần video + ít nhất 2 frame).")
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
        
    lines = [f"{v},{f},{qa_answer}" if is_qa else f"{v},{f}" for v, f in final_results[:total_target]]
    return "\n".join(lines)

def generate_range_csv(video_id, start_frame, end_frame, is_qa, qa_answer, total_target=100):
    frames = []
    if total_target == 1: frames.append(start_frame)
    else:
        step = max(1, (end_frame - start_frame) / (total_target - 1))
        for i in range(total_target):
            f = int(round(start_frame + i * step))
            frames.append(f)
            
    lines = [f"{video_id},{f},{qa_answer}" if is_qa else f"{video_id},{f}" for f in frames[:total_target]]
    return "\n".join(lines)

def generate_trake_csv(video_id, event_frames, total_target=100, step=5):
    """Sinh nhiều biến thể của cả chuỗi N frame sự kiện (TRAKE): mỗi biến thể
    dịch toàn bộ chuỗi frame gốc theo cùng một offset, giữ nguyên khoảng cách
    tương đối giữa các event — giống 'tỏa tròn' nhưng áp dụng cho cả chuỗi."""
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
    lines = [f"{video_id}," + ",".join(str(f) for f in seq) for seq in sequences[:total_target]]
    return "\n".join(lines)

def time_to_sec(t_str):
    try:
        h, m, s = map(int, t_str.split(':'))
        return h*3600 + m*60 + s
    except: return -1

def create_zip_file(db_data):
    """Hàm đóng gói các file CSV đã hoàn thành thành file ZIP"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for q_id, info in db_data.items():
            if info.get("status") == "🟢 Hoàn thành" and info.get("csv_content"):
                file_name = f"{q_id}.csv"
                zip_file.writestr(file_name, info["csv_content"])
    return zip_buffer.getvalue()

# ==========================================
# MÀN HÌNH CHỌN ROLE (LOGIN SCREEN)
# ==========================================
if st.session_state.current_member is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    with col2:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align:center; padding:8px 0 4px 0;">
                {logo_svg(56)}
                <div class="header-eyebrow" style="margin-top:10px;">AIC 2026 · TRẠM LÀM VIỆC</div>
                <h2 style="margin:2px 0 0 0;">Xin chào 👋</h2>
                <div style="color:var(--text-muted);">Chọn tên của bạn để bắt đầu phiên làm việc</div>
            </div>
            """, unsafe_allow_html=True)

            selected_name = st.selectbox("👤 Định danh:", TEAM_MEMBERS)

            if st.button("🚀 Bắt Đầu Làm Việc", type="primary", use_container_width=True):
                st.session_state.current_member = selected_name
                st.rerun()
    st.stop()

current_member = st.session_state.current_member

# ==========================================
# SIDEBAR (NAVIGATION & DASHBOARD)
# ==========================================
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; padding:4px 0 12px 0;">
        {logo_svg(34)}
        <div>
            <div style="font-family:var(--font-display); font-weight:700; font-size:16px; line-height:1.1;">AIC Workspace</div>
            <div style="color:var(--text-muted); font-size:11px;">Video & Keyframe Search 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"👤 Trực ban: **{current_member}**")
        if st.button("🔄 Đổi người", use_container_width=True):
            st.session_state.current_member = None
            st.rerun()
    
    st.divider()
    
    total_queries = len(db)
    completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
    prog = completed_queries / total_queries if total_queries > 0 else 0

    with st.container(border=True):
        st.markdown("**📊 Tiến độ chung**")
        st.progress(prog)
        col_st1, col_st2 = st.columns(2)
        col_st1.metric("Hoàn thành", f"{completed_queries}/{total_queries}")
        col_st2.metric("Tiến độ", f"{int(prog*100)}%")
    
    st.divider()
    selected_menu = st.radio(
        "📍 ĐIỀU HƯỚNG",
        [
            "📋 Quản Lý Query",
            "📤 Upload Nộp Bài",
            "🛠️ Tool Spam Nhanh",
            "📦 Tổng Hợp & Xuất File"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    with st.expander("⚙️ Cài đặt hệ thống"):
        confirm_clear = st.checkbox("Xác nhận xóa DB", key="chk_del")
        if st.button("🧹 Reset Ngày Mới", disabled=not confirm_clear, use_container_width=True):
            st.session_state.db = {}
            save_db({})
            st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH (MAIN AREA)
# ==========================================

if selected_menu == "📋 Quản Lý Query":
    page_header("📋", "Quản Lý & Khởi Tạo Câu Hỏi", "Tạo query mới và theo dõi toàn bộ danh sách nhiệm vụ của đội.")
    col_form, col_list = st.columns([1.2, 1.8], gap="large")
    
    with col_form:
        with st.container(border=True):
            st.subheader("➕ Thêm Query Mới")
            q_name = st.text_input("Tên Query:", placeholder="VD: query-p2-14-kis")
            q_type = st.radio("Loại bài:", ["Textual KIS", "Q&A", "TRAKE"], horizontal=True)
            q_num_events = None
            if q_type == "TRAKE":
                q_num_events = st.number_input("Số lượng events (N) trong chuỗi:", min_value=2, max_value=20, value=4)
            q_desc = st.text_area("Miêu tả video:", placeholder="VĐV mặc áo xanh đua xe...")
            q_raw_data = st.text_area("Dữ liệu truy vấn thô (Dán Top K):", height=130)
            
            if st.button("🚀 Tạo Query Mới", type="primary", use_container_width=True):
                if q_name:
                    db[q_name] = {
                        "type": q_type, "description": q_desc, "raw_data": q_raw_data,
                        "status": "🔴 Chưa làm", "assigned_to": current_member, "csv_content": "",
                        "num_events": int(q_num_events) if q_num_events else None,
                    }
                    save_db(db)
                    st.toast(f"Đã thêm query {q_name} thành công!", icon="✅")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập Tên Query!")

    with col_list:
        st.subheader("📑 Danh Sách Nhiệm Vụ")
        if not db:
            st.info("Chưa có nhiệm vụ nào. Hãy tạo query bên trái!")
        else:
            for q_id, info in list(db.items()):
                with st.container(border=True):
                    c1, c2 = st.columns([0.8, 0.2])
                    type_label = info['type']
                    if info['type'] == "TRAKE" and info.get("num_events"):
                        type_label = f"TRAKE · N={info['num_events']}"
                    c1.markdown(
                        f"{status_badge(info['status'])} &nbsp; **`{q_id}`** <span class='tag-type'>{type_label}</span>",
                        unsafe_allow_html=True
                    )
                    c1.caption(f"📖 {info['description']}  |  *(Tạo bởi: {info.get('assigned_to', 'Ẩn danh')})*")
                    with c2:
                        if st.button("🗑️", key=f"d_{q_id}"): del db[q_id]; save_db(db); st.rerun()
                        if info['status'] == "🟢 Hoàn thành" and st.button("🔄", key=f"r_{q_id}"):
                            db[q_id]["status"] = "🔴 Chưa làm"; save_db(db); st.rerun()

elif selected_menu == "📤 Upload Nộp Bài":
    page_header("📤", "Upload CSV (Validation)", "Dùng khi bạn tự làm file CSV bên ngoài và muốn cập nhật tiến độ.")
    target_q = st.selectbox("Chọn câu cần update:", list(db.keys())) if db else None
    up_file = st.file_uploader("Kéo thả file CSV nộp bài vào đây:", type=['csv'])
    if up_file and target_q:
        file_str = up_file.getvalue().decode("utf-8").strip()
        is_valid, errs = validate_csv_content(file_str, db[target_q]["type"], db[target_q].get("num_events"))
        if is_valid:
            if st.button("Cập nhật tiến độ", type="primary"):
                db[target_q].update({"csv_content": file_str, "status": "🟢 Hoàn thành"})
                save_db(db); st.balloons(); st.rerun()
        else:
            for e in errs: st.error(e)

elif selected_menu == "🛠️ Tool Spam Nhanh":
    page_header("🛠️", "Tool Spam Keyframe Tự Do", "Công cụ độc lập không lưu vào DB — dùng để sinh file test nhanh với tùy chỉnh nâng cao.")
    
    tab_point, tab_range, tab_trake = st.tabs([
        "🎯 Spam Tỏa Tròn (Point Expand)",
        "⏱️ Spam Khoảng Thời Gian (Time Range)",
        "🔗 Spam Chuỗi Sự Kiện (TRAKE)"
    ])
    
    with tab_point:
        col_inp, col_cfg = st.columns([1, 1])
        with col_inp:
            s1_vid = st.text_input("Video ID (VD: L21_V013):", key="s1_vid")
            s1_frames = st.text_area("Các Frame ID gốc (cách nhau dấu phẩy):", key="s1_frames")
            s1_type = st.radio("Loại:", ["Textual KIS", "Q&A"], horizontal=True, key="s1_type")
            s1_qa = st.text_input("Câu trả lời Q&A:") if s1_type == "Q&A" else ""
        with col_cfg:
            s1_total = st.number_input("Tổng số dòng muốn tạo:", min_value=1, max_value=500, value=100)
            s1_step = st.number_input("Bước nhảy (Step Frame):", min_value=1, max_value=50, value=5)
            
            if st.button("🚀 Xuất CSV (Tỏa Tròn)", type="primary", use_container_width=True):
                parsed_f = [int(x) for x in re.findall(r'\d+', s1_frames)]
                if not s1_vid or not parsed_f: st.error("Thiếu thông tin Video ID hoặc Frame.")
                else:
                    csv_out = generate_spam_csv(s1_vid, parsed_f, s1_type == "Q&A", s1_qa, s1_total, s1_step)
                    st.success(f"Tạo thành công {s1_total} dòng!")
                    st.download_button("📥 Tải File CSV Xong", data=csv_out, file_name=f"spam_point_{s1_vid}.csv", mime="text/csv", use_container_width=True)

    with tab_range:
        col_inp2, col_cfg2 = st.columns([1, 1])
        with col_inp2:
            s2_vid = st.text_input("Video ID (VD: L21_V013):", key="s2_vid")
            col_t1, col_t2 = st.columns(2)
            s2_start = col_t1.text_input("Từ thời gian (HH:MM:SS):", placeholder="00:05:00")
            s2_end = col_t2.text_input("Đến thời gian (HH:MM:SS):", placeholder="00:05:15")
            s2_type = st.radio("Loại:", ["Textual KIS", "Q&A"], horizontal=True, key="s2_type")
            s2_qa = st.text_input("Câu trả lời Q&A:", key="s2_qa") if s2_type == "Q&A" else ""
        with col_cfg2:
            s2_fps = st.number_input("FPS của Video (Chuẩn là 25):", min_value=1, max_value=60, value=25)
            s2_total = st.number_input("Tổng số dòng (chia đều):", min_value=1, max_value=500, value=100)
            
            if st.button("🚀 Xuất CSV (Rải Thảm)", type="primary", use_container_width=True):
                sec_start, sec_end = time_to_sec(s2_start), time_to_sec(s2_end)
                if not s2_vid: st.error("Thiếu Video ID!")
                elif sec_start < 0 or sec_end < 0: st.error("Sai định dạng thời gian.")
                elif sec_start >= sec_end: st.error("Thời gian bắt đầu phải < kết thúc!")
                else:
                    frame_start, frame_end = sec_start * s2_fps, sec_end * s2_fps
                    csv_out2 = generate_range_csv(s2_vid, frame_start, frame_end, s2_type == "Q&A", s2_qa, s2_total)
                    st.success(f"Tạo thành công {s2_total} dòng!")
                    st.download_button("📥 Tải File CSV Xong", data=csv_out2, file_name=f"spam_range_{s2_vid}.csv", mime="text/csv", use_container_width=True)

    with tab_trake:
        st.caption("Format: `<Tên file video>, <Frame ID_1>, <Frame ID_2>, ..., <Frame ID_N>` — thứ tự Frame ID phải theo đúng thứ tự thời gian của các event.")
        col_inp3, col_cfg3 = st.columns([1, 1])
        with col_inp3:
            s3_vid = st.text_input("Video ID (VD: L10_V001):", key="s3_vid")
            s3_frames = st.text_area(
                "Frame ID các event, theo thứ tự (cách nhau dấu phẩy):",
                key="s3_frames", placeholder="1200, 1850, 2100, 2450"
            )
        with col_cfg3:
            s3_total = st.number_input("Tổng số dòng muốn tạo:", min_value=1, max_value=500, value=100, key="s3_total")
            s3_step = st.number_input("Bước nhảy (Step, dịch cả chuỗi):", min_value=1, max_value=50, value=5, key="s3_step")

            if st.button("🚀 Xuất CSV (Chuỗi Sự Kiện)", type="primary", use_container_width=True, key="s3_btn"):
                parsed_events = [int(x) for x in re.findall(r'\d+', s3_frames)]
                if not s3_vid or len(parsed_events) < 2:
                    st.error("Thiếu Video ID hoặc cần ít nhất 2 Frame ID sự kiện theo thứ tự.")
                else:
                    csv_out3 = generate_trake_csv(s3_vid, parsed_events, s3_total, s3_step)
                    st.success(f"Tạo thành công {s3_total} dòng, mỗi dòng {len(parsed_events)} event!")
                    st.download_button("📥 Tải File CSV Xong", data=csv_out3, file_name=f"spam_trake_{s3_vid}.csv", mime="text/csv", use_container_width=True)

# ==========================================
# TỔNG HỢP & XUẤT FILE (ZIP)
# ==========================================
elif selected_menu == "📦 Tổng Hợp & Xuất File":
    page_header("📦", "Tổng Hợp & Đóng Gói Bài Nộp", "Kiểm tra tình trạng file và đóng gói toàn bộ bài nộp thành ZIP.")
    
    completed_queries = {k: v for k, v in db.items() if v["status"] == "🟢 Hoàn thành"}
    missing_queries = {k: v for k, v in db.items() if v["status"] == "🔴 Chưa làm"}

    tab_kiemtra, tab_donggoi = st.tabs(["👁️ Kiểm tra tình trạng File", "🗜️ Đóng gói ZIP"])
    
    with tab_kiemtra:
        col_xanh, col_do = st.columns([1, 1])
        
        with col_xanh:
            st.subheader(f"✅ Đã Hoàn Thành ({len(completed_queries)} file)")
            with st.container(border=True):
                if not completed_queries:
                    st.info("Chưa có file nào hoàn thành.")
                else:
                    target_view = st.selectbox("Chọn file để xem nội dung bên trong:", list(completed_queries.keys()))
                    if target_view:
                        st.caption(f"Người làm: **{completed_queries[target_view].get('completed_by', 'Ẩn danh')}**")
                        st.code(completed_queries[target_view]["csv_content"], language="csv")

        with col_do:
            st.subheader(f"⚠️ Còn Thiếu ({len(missing_queries)} file)")
            with st.container(border=True):
                if not missing_queries:
                    st.success("Tuyệt vời! Đã xong toàn bộ.")
                    st.balloons()
                else:
                    for k in missing_queries.keys():
                        st.error(f"🔴 {k}")
                        
    with tab_donggoi:
        st.subheader("🗜️ Đóng gói toàn bộ file nộp")
        st.info("Hệ thống sẽ tự động quét tất cả các câu '🟢 Hoàn thành', tạo thành các file .csv chuẩn và nhét chung vào 1 file nén ZIP.")
        
        if not completed_queries:
            st.warning("⚠️ Chưa có file nào hoàn thành để đóng gói.")
        else:
            col_zip1, col_zip2 = st.columns([1, 1])
            with col_zip1:
                zip_filename = st.text_input("Nhập tên file nén của bạn:", value="submit_lan_1.zip", placeholder="VD: p1_submit.zip")
                if not zip_filename.endswith(".zip"):
                    zip_filename += ".zip"
                
                if st.button("📦 Tạo File ZIP (Đóng gói)", type="primary"):
                    zip_data = create_zip_file(db)
                    st.success(f"🎉 Đã nén thành công {len(completed_queries)} file!")
                    st.download_button(
                        label=f"📥 CLICK ĐỂ TẢI XUỐNG ({zip_filename})",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip",
                        use_container_width=True
                    )
            with col_zip2:
                st.caption("Các file CSV sẽ nằm trong ZIP:")
                for k in completed_queries.keys():
                    st.text(f"📄 {k}.csv")
