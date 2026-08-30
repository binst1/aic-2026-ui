import os
import re
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AIC 2026 - Workspace & Task Manager", page_icon="🎯", layout="wide")

DEFAULT_DIR = r"E:\AIC 2026\28-08-2026"
DB_FILE = "task_database.json"

# -------------------------------------------------------------------
# LƯU TRỮ VÀ QUẢN LÝ DATABASE CÂU HOỎI (TASKS)
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
# BỘ KIỂM ĐỊNH FILE CSV (CSV VALIDATOR)
# -------------------------------------------------------------------
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
                errors.append(f"❌ Dòng {idx+1} sai định dạng KIS (phải có 2 cột: video_id, frame_id). Nội dung: '{line_clean}'")
            else:
                if not parts[0].strip() or not parts[1].strip().isdigit():
                    errors.append(f"❌ Dòng {idx+1} chứa frame_id không phải số hợp lệ: '{parts[1]}'")
        else:  # Q&A
            if len(parts) < 3:
                errors.append(f"❌ Dòng {idx+1} sai định dạng Q&A (phải đủ 3 cột: video_id, frame_id, answer). Nội dung: '{line_clean}'")
            else:
                if not parts[0].strip() or not parts[1].strip().isdigit() or not parts[2].strip():
                    errors.append(f"❌ Dòng {idx+1} chứa dữ liệu Q&A không hợp lệ.")

    return len(errors) == 0, errors

# -------------------------------------------------------------------
# THUẬT TOÁN TẠO CSV 100 DÒNG
# -------------------------------------------------------------------
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
        csv_lines = [f"{v},{f},{qa_answer}" for v, f in final_results]
    else:
        csv_lines = [f"{v},{f}" for v, f in final_results]

    return "\n".join(csv_lines)

# -------------------------------------------------------------------
# SIDEBAR CHÍNH (ĐIỀU HƯỚNG & THÔNG TIN)
# -------------------------------------------------------------------
st.sidebar.title("🎯 AIC 2026 Workspace")

st.sidebar.header("👤 Người Đang Thao Tác")
current_member = st.sidebar.selectbox("Chọn tên bạn:", ["Thành viên 1", "Thành viên 2", "Thành viên 3", "Thành viên 4", "Thành viên 5"])

st.sidebar.divider()

# CHUYỂN 3 MỤC SANG SIDEBAR MENU
st.sidebar.header("📍 MENU CHỨC NĂNG")
selected_menu = st.sidebar.radio(
    "Chọn mục làm việc:",
    [
        "📋 Quản Lý & Khởi Tạo Câu",
        "⚡ Tạo File CSV Spam",
        "📤 Upload & Kiểm Định Nộp Bài"
    ]
)

st.sidebar.divider()
st.sidebar.header("📊 Tiến Độ Toàn Nhóm")

total_queries = len(db)
completed_queries = sum(1 for item in db.values() if item.get("status") == "🟢 Hoàn thành")

if total_queries > 0:
    prog = completed_queries / total_queries
    st.sidebar.progress(prog)
    st.sidebar.metric("Đã làm xong", f"{completed_queries} / {total_queries} câu", f"{prog*100:.1f}%")
else:
    st.sidebar.info("Chưa khởi tạo câu nào.")

st.sidebar.caption("🚀 Hệ thống tự động kiểm tra định dạng 100 dòng chuẩn.")

# -------------------------------------------------------------------
# GIAO DIỆN CHÍNH (THAY ĐỔI THEO MENU SIDEBAR)
# -------------------------------------------------------------------

# MỤC 1: QUẢN LÝ & KHỞI TẠO CÂU
if selected_menu == "📋 Quản Lý & Khởi Tạo Câu":
    st.title("📋 Quản Lý & Khởi Tạo Câu (Query Bank)")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("➕ Thêm Câu Mới / Nhập Truy Vấn")
        q_name = st.text_input("Tên Query (ví dụ: query-p1-8-kis):", value="query-p1-8-kis").strip()
        q_type = st.radio("Loại Task:", ["Textual KIS", "Q&A"], horizontal=True, key="mgr_type")
        q_desc = st.text_area("Đoạn văn miêu tả truy vấn (Query Description):", value="Người đầu bếp lần lượt đặt các miếng nguyên liệu...", height=100)
        q_raw_data = st.text_area("Dữ liệu truy vấn thô / Bảng top kết quả (Dán text vào đây):", value="1   75     0.4472   0.0322581  L26_V171             6061      242.44    L26_V171_037_05", height=100)

        if st.button("📌 Thêm Vào Danh Sách Tiến Độ", type="primary"):
            if not q_name:
                st.error("Vui lòng nhập tên Query!")
            else:
                db[q_name] = {
                    "type": q_type,
                    "description": q_desc,
                    "raw_data": q_raw_data,
                    "status": "🔴 Chưa làm",
                    "assigned_to": current_member,
                    "csv_content": ""
                }
                save_db(db)
                st.success(f"Đã thêm `{q_name}` vào danh sách!")
                st.rerun()

    with col_b:
        st.subheader("📑 Danh Sách Các Câu Đang Quản Lý")
        if not db:
            st.info("Chưa có câu nào trong danh sách.")
        else:
            for query_id, info in list(db.items()):
                status_color = info["status"]
                with st.expander(f"{status_color} **{query_id}** ({info['type']}) - Tạo bởi: {info.get('assigned_to', 'N/A')}"):
                    st.markdown(f"**Miêu tả:**\n{info['description']}")
                    if info['raw_data']:
                        st.caption("Dữ liệu truy vấn kèm theo:")
                        st.code(info['raw_data'])
                    if st.button(f"🗑️ Xóa câu {query_id}", key=f"del_{query_id}"):
                        del db[query_id]
                        save_db(db)
                        st.rerun()

# MỤC 2: TẠO FILE CSV SPAM
elif selected_menu == "⚡ Tạo File CSV Spam":
    st.title("⚡ Tool Spam File CSV (Chuẩn 100 Dòng)")
    
    if not db:
        st.warning("Vui lòng chọn mục '📋 Quản Lý & Khởi Tạo Câu' trên thanh bên trái để thêm câu hỏi trước!")
    else:
        selected_q = st.selectbox("Chọn câu bạn muốn làm:", list(db.keys()))
        q_info = db[selected_q]
        
        st.info(f"📍 **Đang làm:** `{selected_q}` | **Loại:** {q_info['type']} | **Trạng thái:** {q_info['status']}")
        if q_info['description']:
            st.write(f"📖 **Nội dung:** {q_info['description']}")

        c1, c2 = st.columns([1, 1])
        with c1:
            v_id = st.text_input("Video ID (ví dụ: L26_V171):", value="L26_V171").strip()
            frames_input = st.text_area("Các mốc Frame ID nghi ngờ (phân tách bằng dấu phẩy/khoảng trắng):", value="6061, 5437, 5405", height=80)
            
            qa_ans = ""
            if q_info['type'] == "Q&A":
                qa_ans = st.text_input("Câu trả lời Q&A (dùng chung cho 100 dòng):").strip()
            
            if st.button("🚀 Sinh File & Tự Động Kiểm Định Nộp Bài", type="primary"):
                parsed_f = [int(x) for x in re.findall(r'\d+', frames_input)]
                if not v_id or not parsed_f:
                    st.error("Vui lòng nhập Video ID và Frame ID!")
                elif q_info['type'] == "Q&A" and not qa_ans:
                    st.error("Q&A bắt buộc nhập câu trả lời!")
                else:
                    generated_csv = generate_exact_100_csv(v_id, parsed_f, q_info['type'] == "Q&A", qa_ans)
                    
                    db[selected_q]["csv_content"] = generated_csv
                    db[selected_q]["status"] = "🟢 Hoàn thành"
                    db[selected_q]["completed_by"] = current_member
                    save_db(db)

                    if os.path.exists(os.path.dirname(DEFAULT_DIR)):
                        try:
                            os.makedirs(DEFAULT_DIR, exist_ok=True)
                            with open(os.path.join(DEFAULT_DIR, f"{selected_q}.csv"), "w", encoding="utf-8", newline="") as f:
                                f.write(generated_csv)
                        except Exception:
                            pass

                    st.success(f"🎉 Đã làm xong `{selected_q}`! Tiến độ chuyển sang 🟢 **Hoàn thành**.")
                    st.download_button(
                        label=f"📥 Tải File {selected_q}.csv (100 Dòng Chuẩn)",
                        data=generated_csv,
                        file_name=f"{selected_q}.csv",
                        mime="text/csv"
                    )
                    st.rerun()

        with c2:
            st.subheader("👁️ Preview File Đã Làm")
            if q_info.get("csv_content"):
                lines = q_info["csv_content"].split("\n")
                st.code("\n".join(lines[:10]), language="text")
                st.caption(f"Tổng số dòng: {len(lines)} dòng.")
            else:
                st.text("Chưa có dữ liệu CSV cho câu này.")

# MỤC 3: UPLOAD & KIỂM ĐỊNH NỘP BÀI
elif selected_menu == "📤 Upload & Kiểm Định Nộp Bài":
    st.title("📤 Upload File CSV & Auto-Validate Tiến Độ")
    st.caption("Kéo thả file CSV được tạo từ máy ngoài lên đây để hệ thống tự động quét lỗi 100 dòng và tính điểm tiến độ.")

    if not db:
        st.warning("Chưa có danh sách câu trong hệ thống.")
    else:
        target_q_upload = st.selectbox("Chọn câu cần push file CSV nộp:", list(db.keys()), key="up_select")
        uploaded_file = st.file_uploader(f"Kéo thả file CSV cho câu `{target_q_upload}` vào đây:", type=["csv"])

        if uploaded_file is not None:
            file_str = uploaded_file.getvalue().decode("utf-8").strip()
            task_t = db[target_q_upload]["type"]
            
            is_valid, err_list = validate_csv_content(file_str, task_t)
            
            if is_valid:
                st.balloons()
                st.success("✅ **FILE HỢP LỆ VÀ ĐẠT CHUẨN 100 DÒNG!**")
                
                if st.button(f"📥 Xác Nhận Nộp File & Đánh Dấu {target_q_upload} Hoàn Thành", type="primary"):
                    db[target_q_upload]["csv_content"] = file_str
                    db[target_q_upload]["status"] = "🟢 Hoàn thành"
                    db[target_q_upload]["completed_by"] = current_member
                    save_db(db)
                    
                    st.success(f"Đã cập nhật tiến độ câu `{target_q_upload}` sang 🟢 **Hoàn thành** bởi **{current_member}**!")
                    st.rerun()
            else:
                st.error("❌ FILE KHÔNG ĐẠT CHUẨN ĐỊNH DẠNG. CHI TIẾT LỖI:")
                for err in err_list:
                    st.write(err)
