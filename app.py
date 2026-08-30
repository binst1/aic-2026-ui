import os
import re
import json
import pandas as pd
import streamlit as st

# ==========================================
# CẤU HÌNH TRANG & BIẾN MẶC ĐỊNH
# ==========================================
st.set_page_config(page_title="AIC 2026 Workspace", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

DEFAULT_DIR = r"E:\AIC 2026\28-08-2026"
VIDEO_DRIVE_PATH = r"G:\My Drive\AIC_Videos" 
DB_FILE = "task_database.json"
TEAM_MEMBERS = ["VThành", "LThiện", "PThiện", "Nguyên", "NThành"]

st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00a86b; }
    .st-emotion-cache-1v0mbdj.e115fcil1 { border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HÀM XỬ LÝ DỮ LIỆU (Backend)
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

# Biến Session State để lưu người dùng hiện tại
if "current_member" not in st.session_state:
    st.session_state.current_member = None

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

def validate_csv_content(content_str, task_type):
    raw_lines = [line.strip("\r") for line in content_str.split("\n") if line.strip("\r")]
    errors = []
    if len(raw_lines) != 100: errors.append(f"❌ Sai số dòng: Đang có {len(raw_lines)} dòng (Yêu cầu: 100).")
    for idx, line in enumerate(raw_lines):
        parts = line.split(",")
        if task_type == "Textual KIS" and len(parts) != 2: errors.append(f"❌ Dòng {idx+1} sai định dạng KIS.")
        elif task_type == "Q&A" and len(parts) < 3: errors.append(f"❌ Dòng {idx+1} sai định dạng Q&A.")
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
    if total_target == 1:
        frames.append(start_frame)
    else:
        step = max(1, (end_frame - start_frame) / (total_target - 1))
        for i in range(total_target):
            f = int(round(start_frame + i * step))
            frames.append(f)
            
    lines = [f"{video_id},{f},{qa_answer}" if is_qa else f"{video_id},{f}" for f in frames[:total_target]]
    return "\n".join(lines)

def time_to_sec(t_str):
    try:
        h, m, s = map(int, t_str.split(':'))
        return h*3600 + m*60 + s
    except: return -1

# ==========================================
# MÀN HÌNH CHỌN ROLE (LOGIN SCREEN)
# ==========================================
if st.session_state.current_member is None:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    with col2:
        with st.container(border=True):
            st.image("https://cdn-icons-png.flaticon.com/512/9334/9334419.png", width=70)
            st.header("👋 Xin chào!")
            st.markdown("Chào mừng đến với **Trạm Làm Việc AIC 2026**.")
            st.write("Vui lòng chọn tên của bạn để bắt đầu phiên làm việc:")
            
            selected_name = st.selectbox("👤 Định danh:", TEAM_MEMBERS)
            
            if st.button("🚀 Bắt Đầu Làm Việc", type="primary", use_container_width=True):
                st.session_state.current_member = selected_name
                st.rerun()
    st.stop() # Dừng toàn bộ code bên dưới nếu chưa chọn Role

# Gán current_member sau khi đã login thành công
current_member = st.session_state.current_member

# ==========================================
# SIDEBAR (NAVIGATION & DASHBOARD)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9334/9334419.png", width=60) 
    st.title("AIC Workspace")
    
    # Khu vực hiển thị thông tin người dùng
    with st.container(border=True):
        st.markdown(f"👤 Trực ban: **{current_member}**")
        if st.button("🔄 Đổi người", use_container_width=True):
            st.session_state.current_member = None
            st.rerun()
    
    st.divider()
    
    total_queries = len(db)
    completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
    prog = completed_queries / total_queries if total_queries > 0 else 0
    
    st.progress(prog)
    col_st1, col_st2 = st.columns(2)
    col_st1.metric("Hoàn thành", f"{completed_queries}/{total_queries}")
    col_st2.metric("Tiến độ", f"{int(prog*100)}%")
    
    st.divider()
    selected_menu = st.radio(
        "📍 ĐIỀU HƯỚNG",
        ["📋 Quản Lý Query", "🎬 Workflow Tạo CSV", "📤 Upload Nộp Bài", "🛠️ Tool Spam Nhanh"],
        label_visibility="collapsed"
    )

    st.divider()
    with st.expander("⚙️ Cài đặt hệ thống"):
        st.caption(f"Thư mục lưu local:\n`{DEFAULT_DIR}`")
        st.caption(f"Thư mục video:\n`{VIDEO_DRIVE_PATH}`")
        st.markdown("---")
        confirm_clear = st.checkbox("Xác nhận xóa DB", key="chk_del")
        if st.button("🧹 Reset Ngày Mới", disabled=not confirm_clear, use_container_width=True):
            st.session_state.db = {}
            save_db({})
            st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH (MAIN AREA)
# ==========================================

if selected_menu == "📋 Quản Lý Query":
    st.header("📋 Quản Lý & Khởi Tạo Câu Hỏi")
    col_form, col_list = st.columns([1.2, 1.8], gap="large")
    
    with col_form:
        with st.container(border=True):
            st.subheader("➕ Thêm Query Mới")
            q_name = st.text_input("Tên Query:", placeholder="VD: query-p2-14-kis")
            q_type = st.radio("Loại bài:", ["Textual KIS", "Q&A"], horizontal=True)
            q_desc = st.text_area("Miêu tả video:", placeholder="VĐV mặc áo xanh đua xe...")
            q_raw_data = st.text_area("Dữ liệu truy vấn thô (Dán Top K):", height=130)
            
            if st.button("🚀 Tạo Query Mới", type="primary", use_container_width=True):
                if q_name:
                    db[q_name] = {"type": q_type, "description": q_desc, "raw_data": q_raw_data, "status": "🔴 Chưa làm", "assigned_to": current_member, "csv_content": ""}
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
                    c1.markdown(f"**{info['status']} | `{q_id}`** ({info['type']})")
                    c1.caption(f"📖 {info['description']}  |  *(Tạo bởi: {info.get('assigned_to', 'Ẩn danh')})*")
                    with c2:
                        if st.button("🗑️", key=f"d_{q_id}"): del db[q_id]; save_db(db); st.rerun()
                        if info['status'] == "🟢 Hoàn thành" and st.button("🔄", key=f"r_{q_id}"):
                            db[q_id]["status"] = "🔴 Chưa làm"; save_db(db); st.rerun()

elif selected_menu == "🎬 Workflow Tạo CSV":
    st.header("🎬 Workflow: Soi Video & Tự Động Tạo CSV")
    if not db:
        st.warning("⚠️ Danh sách trống. Hãy tạo Query ở mục Quản lý trước!")
    else:
        selected_q = st.selectbox("🎯 Đang xử lý:", list(db.keys()))
        q_info = db[selected_q]
        st.markdown(f"*{q_info['description']}*")

        if "auto_vid" not in st.session_state: st.session_state.auto_vid = ""
        if "auto_frame" not in st.session_state: st.session_state.auto_frame = ""

        col_video, col_tool = st.columns([1.5, 1], gap="medium")

        with col_video:
            with st.container(border=True):
                st.subheader("🔍 Khung Nhìn Trực Tiếp")
                parsed_results = parse_raw_data(q_info['raw_data'])
                if not parsed_results:
                    st.error("Không trích xuất được dữ liệu thô. Hãy dán lại chuẩn format.")
                else:
                    options = [f"Top {i+1} | 🎬 {r['video_id']} | ⏱ {r['time_str']} (Frame {r['frame']})" for i, r in enumerate(parsed_results)]
                    selected_opt = st.selectbox("Chọn mốc thời gian để soi:", options)
                    
                    curr_res = parsed_results[options.index(selected_opt)]
                    vid_id, target_sec, target_frame = curr_res['video_id'], curr_res['seconds'], curr_res['frame']
                    vid_path = os.path.join(VIDEO_DRIVE_PATH, f"{vid_id}.mp4")
                    
                    if os.path.exists(vid_path):
                        st.video(vid_path, start_time=target_sec)
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("✨ ĐÚNG FRAME NÀY! AUTO-FILL SANG CSV", type="primary", use_container_width=True):
                            st.session_state.auto_vid = vid_id
                            if st.session_state.auto_frame == "": st.session_state.auto_frame = str(target_frame)
                            else: st.session_state.auto_frame += f", {target_frame}"
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Không tìm thấy file `{vid_id}.mp4` trong ổ đĩa ảo!")

        with col_tool:
            with st.container(border=True):
                st.subheader("⚡ Tool Spam KIS/QA")
                v_id = st.text_input("Video ID:", value=st.session_state.auto_vid)
                frames_input = st.text_area("Các mốc Frame:", value=st.session_state.auto_frame, height=100)
                qa_ans = st.text_input("Câu trả lời (Nếu là Q&A):") if q_info['type'] == "Q&A" else ""
                
                if st.button("🔥 Sinh File & Lưu Vào DB", use_container_width=True):
                    parsed_f = [int(x) for x in re.findall(r'\d+', frames_input)]
                    if not v_id or not parsed_f: st.error("Thiếu Video/Frame ID!")
                    else:
                        generated_csv = generate_spam_csv(v_id, parsed_f, q_info['type'] == "Q&A", qa_ans, 100, 5)
                        db[selected_q].update({"csv_content": generated_csv, "status": "🟢 Hoàn thành", "completed_by": current_member})
                        save_db(db)
                        st.session_state.auto_vid, st.session_state.auto_frame = "", ""
                        st.success("Lưu DB thành công!")
                        st.download_button("📥 Click tải CSV về máy", data=generated_csv, file_name=f"{selected_q}.csv", mime="text/csv", use_container_width=True)
                        st.rerun()

elif selected_menu == "📤 Upload Nộp Bài":
    st.header("📤 Upload CSV (Validation)")
    st.caption("Dùng chức năng này khi bạn tự làm file CSV bên ngoài và muốn cập nhật tiến độ.")
    target_q = st.selectbox("Chọn câu cần update:", list(db.keys())) if db else None
    up_file = st.file_uploader("Kéo thả file CSV nộp bài vào đây:", type=['csv'])
    if up_file and target_q:
        file_str = up_file.getvalue().decode("utf-8").strip()
        is_valid, errs = validate_csv_content(file_str, db[target_q]["type"])
        if is_valid:
            if st.button("Cập nhật tiến độ", type="primary"):
                db[target_q].update({"csv_content": file_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                save_db(db); st.balloons(); st.rerun()
        else:
            for e in errs: st.error(e)

elif selected_menu == "🛠️ Tool Spam Nhanh":
    st.header("🛠️ Tool Spam Keyframe Tự Do")
    st.caption("Công cụ độc lập không lưu vào DB. Dùng để sinh file test nhanh với các tùy chỉnh nâng cao.")
    
    tab_point, tab_range = st.tabs(["🎯 Spam Tỏa Tròn (Point Expand)", "⏱️ Spam Khoảng Thời Gian (Time Range)"])
    
    with tab_point:
        st.info("Nhập 1 hoặc nhiều mốc Frame. Tool sẽ tỏa ra xung quanh (Cộng/Trừ step) cho đến khi đủ số dòng.")
        col_inp, col_cfg = st.columns([1, 1])
        with col_inp:
            s1_vid = st.text_input("Video ID (VD: L21_V013):", key="s1_vid")
            s1_frames = st.text_area("Các Frame ID gốc (cách nhau bởi dấu phẩy):", key="s1_frames")
            s1_type = st.radio("Loại:", ["Textual KIS", "Q&A"], horizontal=True, key="s1_type")
            s1_qa = st.text_input("Câu trả lời Q&A:") if s1_type == "Q&A" else ""
        with col_cfg:
            s1_total = st.number_input("Tổng số dòng muốn tạo:", min_value=1, max_value=500, value=100)
            s1_step = st.number_input("Bước nhảy (Step Frame):", min_value=1, max_value=50, value=5)
            
            if st.button("🚀 Xuất CSV (Tỏa Tròn)", type="primary", use_container_width=True):
                parsed_f = [int(x) for x in re.findall(r'\d+', s1_frames)]
                if not s1_vid or not parsed_f:
                    st.error("Thiếu thông tin Video ID hoặc Frame.")
                else:
                    csv_out = generate_spam_csv(s1_vid, parsed_f, s1_type == "Q&A", s1_qa, s1_total, s1_step)
                    st.success(f"Tạo thành công {s1_total} dòng!")
                    st.download_button("📥 Tải File CSV Xong", data=csv_out, file_name=f"spam_point_{s1_vid}.csv", mime="text/csv", use_container_width=True)
                    with st.expander("👁️ Xem trước kết quả"): st.code(csv_out)

    with tab_range:
        st.info("Bạn biết sự kiện nằm trong khoảng thời gian từ A đến B? Nhập vào đây, hệ thống rải đều frame ra toàn bộ khoảng đó!")
        col_inp2, col_cfg2 = st.columns([1, 1])
        with col_inp2:
            s2_vid = st.text_input("Video ID (VD: L21_V013):", key="s2_vid")
            col_t1, col_t2 = st.columns(2)
            s2_start = col_t1.text_input("Từ thời gian (HH:MM:SS):", placeholder="00:05:00")
            s2_end = col_t2.text_input("Đến thời gian (HH:MM:SS):", placeholder="00:05:15")
            s2_type = st.radio("Loại:", ["Textual KIS", "Q&A"], horizontal=True, key="s2_type")
            s2_qa = st.text_input("Câu trả lời Q&A:", key="s2_qa") if s2_type == "Q&A" else ""
        with col_cfg2:
            s2_fps = st.number_input("FPS của Video (Chuẩn AIC là 25):", min_value=1, max_value=60, value=25)
            s2_total = st.number_input("Tổng số dòng (chia đều):", min_value=1, max_value=500, value=100)
            
            if st.button("🚀 Xuất CSV (Rải Thảm)", type="primary", use_container_width=True):
                sec_start = time_to_sec(s2_start)
                sec_end = time_to_sec(s2_end)
                
                if not s2_vid: st.error("Thiếu Video ID!")
                elif sec_start < 0 or sec_end < 0: st.error("Sai định dạng thời gian. Vui lòng nhập HH:MM:SS")
                elif sec_start >= sec_end: st.error("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc!")
                else:
                    frame_start = sec_start * s2_fps
                    frame_end = sec_end * s2_fps
                    st.toast(f"Khoảng Frame nội suy: {frame_start} đến {frame_end}", icon="📐")
                    
                    csv_out2 = generate_range_csv(s2_vid, frame_start, frame_end, s2_type == "Q&A", s2_qa, s2_total)
                    st.success(f"Tạo thành công {s2_total} dòng (rải đều từ frame {frame_start} - {frame_end})!")
                    st.download_button("📥 Tải File CSV Xong", data=csv_out2, file_name=f"spam_range_{s2_vid}.csv", mime="text/csv", use_container_width=True)
                    with st.expander("👁️ Xem trước kết quả"): st.code(csv_out2)
