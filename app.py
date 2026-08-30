import os
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AIC 2026 - Team Workspace", page_icon="👥", layout="wide")

DEFAULT_DIR = r"E:\AIC 2026\28-08-2026"

# -------------------------------------------------------------------
# THUẬT TOÁN TẠO CSV EXATCT 100 LINES
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
# GIAO DIỆN HỆ THỐNG
# -------------------------------------------------------------------
st.title("🌐 AIC 2026 - Online Team WorkStation")

# SIDEBAR: THÀNH VIÊN
st.sidebar.header("👤 Người Thực Hiện")
current_member = st.sidebar.selectbox("Bạn là ai?", ["Thành viên 1", "Thành viên 2", "Thành viên 3", "Thành viên 4", "Thành viên 5"])

st.sidebar.divider()
st.sidebar.info("💡 **Mẹo:** Sau khi xuất file thành công, hãy tải file CSV về và đẩy lên thư mục Google Drive chung của nhóm.")

# MAIN AREA
col_form, col_preview = st.columns([1, 1])

with col_form:
    st.subheader("📝 Nhập Bài Làm")
    
    filename = st.text_input("Tên File CSV xuất ra (ví dụ: query-p2-1.csv):").strip()
    if filename and not filename.endswith(".csv"):
        filename += ".csv"

    task_type = st.radio("Loại Task:", ["Textual KIS", "Q&A"], horizontal=True)
    is_qa = (task_type == "Q&A")
    
    qa_answer = ""
    if is_qa:
        qa_answer = st.text_input("Nhập câu trả lời Q&A (dùng chung 100 dòng):").strip()

    video_id = st.text_input("Video ID (ví dụ: L21_V013):").strip()
    frames_str = st.text_area("Danh sách Frame ID (nhập các số cách nhau bởi dấu phẩy):", height=80)

    btn_create = st.button("🚀 Tạo Nội Dung CSV", type="primary", use_container_width=True)

with col_preview:
    st.subheader("👁️ Kiểm Tra & Tải File")
    
    parsed_frames = [int(x) for x in re.findall(r'\d+', frames_str)]
    if parsed_frames:
        st.info(f"Phát hiện **{len(parsed_frames)}** mốc frame. Mỗi mốc chia **{100 // len(parsed_frames)}** slots.")
    
    if btn_create:
        if not filename or not video_id or not parsed_frames:
            st.error("❌ Vui lòng điền đầy đủ Tên File, Video ID và ít nhất 1 Frame ID!")
        elif is_qa and not qa_answer:
            st.error("❌ Bài Q&A bắt buộc phải nhập câu trả lời!")
        else:
            file_content = generate_exact_100_csv(video_id, parsed_frames, is_qa, qa_answer)
            
            # Nếu chạy dưới local thì thử tự ghi vào ổ E:\
            if os.path.exists(os.path.dirname(DEFAULT_DIR)):
                try:
                    os.makedirs(DEFAULT_DIR, exist_ok=True)
                    with open(os.path.join(DEFAULT_DIR, filename), "w", encoding="utf-8", newline="") as f:
                        f.write(file_content)
                    st.success(f"✅ Đã tự động lưu một bản vào ổ E: `{DEFAULT_DIR}\\{filename}`")
                except Exception:
                    pass

            st.success(f"✅ **{current_member}** đã tạo thành công file `{filename}` (Đúng 100 dòng)!")
            
            # Nút tải file về máy
            st.download_button(
                label=f"📥 TẢI FILE {filename} VỀ MÁY CÁ NHÂN",
                data=file_content,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
            
            st.text("📄 Xem trước 5 dòng đầu:")
            st.code("\n".join(file_content.split("\n")[:5]))
            st.text("📄 Xem trước 3 dòng cuối (Kiểm tra dòng thừa):")
            lines = file_content.split("\n")
            st.code(f"Dòng 98: {lines[-3]}\nDòng 99: {lines[-2]}\nDòng 100: {lines[-1]}")