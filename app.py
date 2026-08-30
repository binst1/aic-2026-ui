import os
import re
import json
import pandas as pd
import streamlit as st

# ==========================================
# CẤU HÌNH TRANG & BIẾN MẶC ĐỊNH
# ==========================================
st.set_page_config(page_title="AIC 2026 Workspace", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ẨN CẤU HÌNH VÀO CODE (KHÔNG HIỆN TRÊN UI NỮA)
DEFAULT_DIR = r"E:\AIC 2026\28-08-2026"
VIDEO_DRIVE_PATH = r"G:\My Drive\AIC_Videos" # Sửa đường dẫn ổ đĩa video thật của bạn ở đây
DB_FILE = "task_database.json"

# Custom CSS để làm đẹp giao diện
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00a86b; }
    .st-emotion-cache-1v0mbdj.e115fcil1 { border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HÀM XỬ LÝ DỮ LIỆU BÊN DƯỚI (Backend)
# ==========================================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_db()

db = st.session_state.db

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

def generate_exact_100_csv(video_id, input_frames, is_qa, qa_answer):
    total_target = 100
    base_quota = total_target // len(input_frames)
    remainder = total_target % len(input_frames)
    quotas = [base_quota + (1 if i < remainder else 0) for i in range(len(input_frames))]
    
    seen, final_results = set(), []
    for i, base_frame in enumerate(input_frames):
        curr, offset = [], 5
        if (video_id, base_frame) not in seen:
            seen.add((video_id, base_frame)); curr.append((video_id, base_frame))
        while len(curr) < quotas[i]:
            for df in [offset, -offset]:
                f_new = base_frame + df
                if f_new >= 0 and (video_id, f_new) not in seen and len(curr) < quotas[i]:
                    seen.add((video_id, f_new)); curr.append((video_id, f_new))
            offset += 5
        final_results.extend(curr)
        
    return "\n".join([f"{v},{f},{qa_answer}" if is_qa else f"{v},{f}" for v, f in final_results[:100]])

# ==========================================
# SIDEBAR (NAVIGATION & DASHBOARD)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9334/9334419.png", width=60) # Logo giả lập
    st.title("AIC Workspace")
    
    # 1. Thống kê tiến độ trực quan
    total_queries = len(db)
    completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
    prog = completed_queries / total_queries if total_queries > 0 else 0
    
    st.progress(prog)
    col_st1, col_st2 = st.columns(2)
    col_st1.metric("Hoàn thành", f"{completed_queries}/{total_queries}")
    col_st2.metric("Tiến độ", f"{int(prog*100)}%")
    
    st.divider()

    # 2. Định danh người dùng
    current_member = st.selectbox("👤 Trực ban:", ["Thành viên 1", "Thành viên 2", "Thành viên 3", "Thành viên 4", "Thành viên 5"])
    
    st.divider()

    # 3. Menu điều hướng (Gọn gàng)
    selected_menu = st.radio(
        "📍 ĐIỀU HƯỚNG",
        ["📋 Quản Lý Query", "🎬 Workflow Tạo CSV", "📤 Upload Nộp Bài"],
        label_visibility="collapsed"
    )

    st.divider()

    # 4. Giấu mục Reset Data vào Cài đặt
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
            q_raw_data = st.text_area("Dữ liệu truy vấn thô (Dán Top K):", height=130, placeholder="1   95     92.73     1.00     1.00  L23_V024\n    1: frame=7642 time=00:05:05...")
            
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
                    c1.caption(f"📖 {info['description']}")
                    
                    with c2:
                        if st.button("🗑️", key=f"d_{q_id}", help="Xóa query này"): 
                            del db[q_id]; save_db(db); st.rerun()
                        if info['status'] == "🟢 Hoàn thành" and st.button("🔄", key=f"r_{q_id}", help="Đặt lại trạng thái"):
                            db[q_id]["status"] = "🔴 Chưa làm"; save_db(db); st.rerun()

elif selected_menu == "🎬 Workflow Tạo CSV":
    st.header("🎬 Workflow: Soi Video & Tự Động Tạo CSV")
    
    if not db:
        st.warning("⚠️ Danh sách trống. Hãy tạo Query ở mục Quản lý trước!")
    else:
        # Thanh chọn nhanh Query
        selected_q = st.selectbox("🎯 Đang xử lý:", list(db.keys()))
        q_info = db[selected_q]
        st.markdown(f"*{q_info['description']}*")

        if "auto_vid" not in st.session_state: st.session_state.auto_vid = ""
        if "auto_frame" not in st.session_state: st.session_state.auto_frame = ""

        # Layout Mới: Trái Video rộng hơn, Phải Tool hẹp hơn
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
                    
                    opt_idx = options.index(selected_opt)
                    curr_res = parsed_results[opt_idx]
                    vid_id, target_sec, target_frame = curr_res['video_id'], curr_res['seconds'], curr_res['frame']

                    vid_path = os.path.join(VIDEO_DRIVE_PATH, f"{vid_id}.mp4")
                    
                    if os.path.exists(vid_path):
                        st.video(vid_path, start_time=target_sec)
                        
                        # Nút Bắt Frame Nổi Bật
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("✨ ĐÚNG FRAME NÀY! AUTO-FILL SANG CSV", type="primary", use_container_width=True):
                            st.session_state.auto_vid = vid_id
                            if st.session_state.auto_frame == "":
                                st.session_state.auto_frame = str(target_frame)
                            else:
                                st.session_state.auto_frame += f", {target_frame}"
                            st.toast("Đã chuyển data sang tool tạo CSV!", icon="🚀")
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Video không khả dụng: Không tìm thấy `{vid_id}.mp4` tại đường dẫn:\n `{VIDEO_DRIVE_PATH}`\n*(Hãy kiểm tra lại ổ đĩa hoặc file tải về)*")

        with col_tool:
            with st.container(border=True):
                st.subheader("⚡ Tool Spam KIS/QA")
                v_id = st.text_input("Video ID:", value=st.session_state.auto_vid, placeholder="L23_V024")
                frames_input = st.text_area("Các mốc Frame:", value=st.session_state.auto_frame, height=100, placeholder="7642, 8000...")
                
                qa_ans = ""
                if q_info['type'] == "Q&A":
                    qa_ans = st.text_input("Câu trả lời (Q&A):", placeholder="VD: màu xanh")
                
                if st.button("🔥 Sinh File 100 Dòng", use_container_width=True):
                    parsed_f = [int(x) for x in re.findall(r'\d+', frames_input)]
                    if not v_id or not parsed_f: st.error("Thiếu Video ID hoặc Frame ID!")
                    elif q_info['type'] == "Q&A" and not qa_ans: st.error("Thiếu câu trả lời cho Q&A!")
                    else:
                        generated_csv = generate_exact_100_csv(v_id, parsed_f, q_info['type'] == "Q&A", qa_ans)
                        db[selected_q].update({"csv_content": generated_csv, "status": "🟢 Hoàn thành", "completed_by": current_member})
                        save_db(db)
                        
                        st.session_state.auto_vid = ""
                        st.session_state.auto_frame = ""
                        st.success("Tạo file thành công!")
                        
                        st.download_button("📥 Click tải CSV về máy", data=generated_csv, file_name=f"{selected_q}.csv", mime="text/csv", use_container_width=True)
                        st.rerun()

elif selected_menu == "📤 Upload Nộp Bài":
    st.header("📤 Upload CSV (Validation)")
    st.caption("Dùng chức năng này khi bạn tự làm file CSV bên ngoài và muốn cập nhật tiến độ.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        target_q = st.selectbox("Chọn câu cần update:", list(db.keys())) if db else None
        up_file = st.file_uploader("Kéo thả file CSV nộp bài vào đây:", type=['csv'])
        
        if up_file and target_q:
            file_str = up_file.getvalue().decode("utf-8").strip()
            is_valid, errs = validate_csv_content(file_str, db[target_q]["type"])
            if is_valid:
                st.success("✅ File hợp lệ, chuẩn 100 dòng!")
                if st.button("Cập nhật tiến độ hệ thống", type="primary"):
                    db[target_q].update({"csv_content": file_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                    save_db(db)
                    st.balloons()
                    st.toast("Đã cập nhật tiến độ!", icon="🎉")
                    st.rerun()
            else:
                for e in errs: st.error(e)
