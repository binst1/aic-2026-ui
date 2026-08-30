import os
import re
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AIC 2026 - Workspace & Task Manager", page_icon="🎯", layout="wide")

DEFAULT_DIR = r"E:\AIC 2026\28-08-2026"
DB_FILE = "task_database.json"

# -------------------------------------------------------------------
# LƯU TRỮ VÀ QUẢN LÝ DATABASE CÂU HOỎI
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# BỘ CÔNG CỤ XỬ LÝ (PARSE DATA & CSV)
# -------------------------------------------------------------------
def parse_raw_data(raw_data):
    """Đọc dữ liệu thô và trích xuất Video ID, Frame, Thời gian"""
    results = []
    lines = raw_data.strip().split('\n')
    current_vid = None
    
    for line in lines:
        # Tìm Video ID (VD: L23_V024)
        vid_match = re.search(r'(L\d+_V\d+)', line)
        if vid_match and 'keyframe' not in line:
            current_vid = vid_match.group(1)
        
        # Tìm Frame và Time (VD: frame=7642 time=00:05:05)
        time_match = re.search(r'frame=(\d+)\s+time=(\d{2}:\d{2}:\d{2})', line)
        if time_match and current_vid:
            frame = time_match.group(1)
            time_str = time_match.group(2)
            h, m, s = map(int, time_str.split(':'))
            total_sec = h * 3600 + m * 60 + s
            results.append({
                "video_id": current_vid,
                "frame": frame,
                "time_str": time_str,
                "seconds": total_sec
            })
            current_vid = None # reset cho dòng tiếp theo
            
    return results

def validate_csv_content(content_str, task_type):
    raw_lines = content_str.split("\n")
    if raw_lines and raw_lines[-1] == "":
        raw_lines.pop()

    errors = []
    if len(raw_lines) != 100:
        errors.append(f"❌ Số dòng không chính xác 100 dòng (Đang có: {len(raw_lines)} dòng).")

    for idx, line in enumerate(raw_lines):
        line_clean = line.strip("\r")
        if not line_clean:
            errors.append(f"❌ Dòng {idx+1} bị trống.")
            continue
        parts = line_clean.split(",")
        if task_type == "Textual KIS":
            if len(parts) != 2:
                errors.append(f"❌ Dòng {idx+1} sai định dạng KIS")
        else: 
            if len(parts) < 3:
                errors.append(f"❌ Dòng {idx+1} sai định dạng Q&A")
    return len(errors) == 0, errors

def generate_exact_100_csv(video_id, input_frames, is_qa, qa_answer):
    num_frames = len(input_frames)
    total_target = 100
    base_quota = total_target // num_frames
    remainder = total_target % num_frames
    quotas = [base_quota + (1 if i < remainder else 0) for i in range(num_frames)]

    step = 5
    per_frame_expanded = []
    seen = set()

    for i, base_frame in enumerate(input_frames):
        quota = quotas[i]
        curr = []
        if (video_id, base_frame) not in seen:
            seen.add((video_id, base_frame))
            curr.append((video_id, base_frame))
        
        offset = step
        while len(curr) < quota:
            f_plus = base_frame + offset
            if (video_id, f_plus) not in seen and len(curr) < quota:
                seen.add((video_id, f_plus))
                curr.append((video_id, f_plus))
            f_minus = base_frame - offset
            if f_minus >= 0 and (video_id, f_minus) not in seen and len(curr) < quota:
                seen.add((video_id, f_minus))
                curr.append((video_id, f_minus))
            offset += step
        per_frame_expanded.append(curr)

    final_results = []
    max_len = max(len(sub) for sub in per_frame_expanded) if per_frame_expanded else 0
    for row_idx in range(max_len):
        for sub in per_frame_expanded:
            if row_idx < len(sub) and len(final_results) < total_target:
                final_results.append(sub[row_idx])

    if is_qa:
        return "\n".join([f"{v},{f},{qa_answer}" for v, f in final_results])
    return "\n".join([f"{v},{f}" for v, f in final_results])

# -------------------------------------------------------------------
# SIDEBAR CHÍNH (ĐIỀU HƯỚNG & CẤU HÌNH)
# -------------------------------------------------------------------
st.sidebar.title("🎯 AIC 2026 Workspace")

st.sidebar.header("⚙️ Cấu Hình Máy Local")
# Thêm đường dẫn tới ổ chứa Video (Người dùng tự trỏ tới ổ D, E...)
video_drive_path = st.sidebar.text_input("📁 Thư mục chứa Video (.mp4):", value=r"D:\AIC_Videos").strip()

st.sidebar.divider()
st.sidebar.header("👤 Người Đang Thao Tác")
current_member = st.sidebar.selectbox("Chọn tên bạn:", ["Thành viên 1", "Thành viên 2", "Thành viên 3", "Thành viên 4", "Thành viên 5"])

st.sidebar.divider()
st.sidebar.header("📍 MENU CHỨC NĂNG")
selected_menu = st.sidebar.radio(
    "Chọn mục làm việc:",
    [
        "📋 Quản Lý & Khởi Tạo Câu",
        "🎬 Review Video & Tạo CSV",
        "📤 Upload & Kiểm Định Nộp Bài"
    ]
)

st.sidebar.divider()
total_queries = len(db)
completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")
if total_queries > 0:
    st.sidebar.progress(completed_queries / total_queries)
    st.sidebar.metric("Tiến độ Nhóm", f"{completed_queries} / {total_queries} câu")

confirm_clear = st.sidebar.checkbox("Xác nhận xóa sạch DB")
if st.sidebar.button("🧹 Reset Data (Ngày Mới)", disabled=not confirm_clear):
    st.session_state.db = {}
    save_db({})
    st.rerun()


# -------------------------------------------------------------------
# GIAO DIỆN CHÍNH
# -------------------------------------------------------------------

# MỤC 1: QUẢN LÝ
if selected_menu == "📋 Quản Lý & Khởi Tạo Câu":
    st.title("📋 Quản Lý & Khởi Tạo Câu (Query Bank)")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("➕ Thêm Query")
        q_name = st.text_input("Tên Query:", value="query-p2-14-kis")
        q_type = st.radio("Loại Task:", ["Textual KIS", "Q&A"], horizontal=True)
        q_desc = st.text_area("Miêu tả truy vấn:")
        q_raw_data = st.text_area("Dữ liệu truy vấn thô (Dán kết quả Top K vào đây):", height=150, 
            help="Dán y nguyên kết quả truy vấn chứa Video ID, Frame, Time...")
        if st.button("📌 Thêm Vào Database", type="primary"):
            if q_name:
                db[q_name] = {"type": q_type, "description": q_desc, "raw_data": q_raw_data, "status": "🔴 Chưa làm", "assigned_to": current_member, "csv_content": ""}
                save_db(db)
                st.success("Đã thêm!")
                st.rerun()
    with c2:
        st.subheader("📑 Danh Sách Câu")
        for q_id, info in list(db.items()):
            with st.expander(f"{info['status']} {q_id} ({info['type']})"):
                st.write(info['description'])
                col_del, col_re = st.columns(2)
                if col_del.button("🗑️ Xóa", key=f"d_{q_id}"): del db[q_id]; save_db(db); st.rerun()
                if info['status'] == "🟢 Hoàn thành" and col_re.button("🔄 Làm lại", key=f"r_{q_id}"):
                    db[q_id]["status"] = "🔴 Chưa làm"; save_db(db); st.rerun()

# MỤC 2: REVIEW VIDEO & TẠO CSV (ĐÃ TỐI ƯU WORKFLOW)
elif selected_menu == "🎬 Review Video & Tạo CSV":
    st.title("🎬 Workflow Tối Ưu: Kiểm Tra Video & Auto-CSV")
    
    if not db:
        st.warning("Vui lòng thêm câu hỏi ở mục Quản Lý trước!")
    else:
        selected_q = st.selectbox("🎯 Chọn câu muốn giải quyết:", list(db.keys()))
        q_info = db[selected_q]
        st.info(f"**Miêu tả:** {q_info['description']}")

        # Khởi tạo Session State cho Autofill
        if "auto_vid" not in st.session_state: st.session_state.auto_vid = ""
        if "auto_frame" not in st.session_state: st.session_state.auto_frame = ""

        # Chia màn hình làm 2 cột: Cột trái xem Video, Cột phải tạo CSV
        col_video, col_csv = st.columns([1.2, 0.8])

        with col_video:
            st.subheader("🔍 Review Video Nhanh")
            
            # Tự động đọc Raw Data
            parsed_results = parse_raw_data(q_info['raw_data'])
            
            if not parsed_results:
                st.error("⚠️ Không tìm thấy dữ liệu chuẩn trong Raw Data. Vui lòng check lại cú pháp lúc khai báo.")
            else:
                # Tạo bảng chọn kết quả để xem video
                options = [f"Top {i+1}: {r['video_id']} - {r['time_str']} (Frame: {r['frame']})" for i, r in enumerate(parsed_results)]
                selected_opt = st.selectbox("Tự động trích xuất các mốc nghi ngờ, hãy chọn 1 mốc để xem:", options)
                
                # Lấy dữ liệu của lựa chọn hiện tại
                opt_idx = options.index(selected_opt)
                curr_res = parsed_results[opt_idx]
                vid_id = curr_res['video_id']
                target_sec = curr_res['seconds']
                target_frame = curr_res['frame']

                # KIỂM TRA FILE VIDEO LOCAL VÀ PHÁT
                vid_path = os.path.join(video_drive_path, f"{vid_id}.mp4")
                
                if os.path.exists(vid_path):
                    st.video(vid_path, start_time=target_sec)
                    st.success(f"▶️ Đang phát `{vid_id}.mp4` tại **{curr_res['time_str']}** (Giây thứ {target_sec})")
                else:
                    st.error(f"❌ Không tìm thấy file `{vid_path}` trong ổ cứng. Hãy kiểm tra lại cấu hình đường dẫn ở Sidebar.")
                
                # Nút ma thuật: Bấm 1 phát là đưa data sang cột tạo CSV
                if st.button("👉 CHUẨN RỒI! DÙNG VIDEO VÀ FRAME NÀY ĐỂ TẠO CSV", type="primary"):
                    st.session_state.auto_vid = vid_id
                    
                    # Nối thêm frame vào danh sách nếu muốn kết hợp nhiều frame, hoặc ghi đè
                    if st.session_state.auto_frame == "":
                        st.session_state.auto_frame = str(target_frame)
                    else:
                        st.session_state.auto_frame += f", {target_frame}"
                    st.rerun()

        with col_csv:
            st.subheader("⚡ Tool Spam CSV 100 Dòng")
            with st.container(border=True):
                # Các ô nhập liệu sẽ tự động lấy từ Session State nếu có
                v_id = st.text_input("Video ID:", value=st.session_state.auto_vid)
                frames_input = st.text_area("Các mốc Frame (tự động điền hoặc sửa tay):", value=st.session_state.auto_frame, height=80)
                
                qa_ans = ""
                if q_info['type'] == "Q&A":
                    qa_ans = st.text_input("Câu trả lời Q&A:").strip()
                
                if st.button("🚀 Sinh File & Nộp Lên Hệ Thống", type="primary", use_container_width=True):
                    parsed_f = [int(x) for x in re.findall(r'\d+', frames_input)]
                    if not v_id or not parsed_f:
                        st.error("Thiếu Video ID hoặc Frame!")
                    elif q_info['type'] == "Q&A" and not qa_ans:
                        st.error("Q&A bắt buộc nhập câu trả lời!")
                    else:
                        generated_csv = generate_exact_100_csv(v_id, parsed_f, q_info['type'] == "Q&A", qa_ans)
                        
                        db[selected_q]["csv_content"] = generated_csv
                        db[selected_q]["status"] = "🟢 Hoàn thành"
                        save_db(db)
                        
                        st.success("🎉 Tạo thành công 100 dòng chuẩn!")
                        st.download_button("📥 Tải CSV", data=generated_csv, file_name=f"{selected_q}.csv", mime="text/csv", use_container_width=True)
                        
                        # Reset autofill
                        st.session_state.auto_vid = ""
                        st.session_state.auto_frame = ""

# MỤC 3: UPLOAD CSV NGOÀI (Giữ nguyên thuật toán Validation)
elif selected_menu == "📤 Upload & Kiểm Định Nộp Bài":
    st.title("📤 Upload CSV & Kiểm Định")
    target_q = st.selectbox("Chọn câu:", list(db.keys())) if db else None
    up_file = st.file_uploader("Kéo thả CSV:")
    
    if up_file and target_q:
        file_str = up_file.getvalue().decode("utf-8").strip()
        is_valid, errs = validate_csv_content(file_str, db[target_q]["type"])
        if is_valid:
            st.success("✅ File chuẩn 100 dòng!")
            if st.button("Cập nhật Tiến độ"):
                db[target_q].update({"csv_content": file_str, "status": "🟢 Hoàn thành", "completed_by": current_member})
                save_db(db); st.rerun()
        else:
            for e in errs: st.error(e)
