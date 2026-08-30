import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 1. CẤU HÌNH & KHỞI TẠO THƯ MỤC
# ==============================================================================
st.set_page_config(page_title="AI Challenge Query Manager", layout="wide")

QUERY_DIR = "data/queries"
SUBMISSION_DIR = "data/submissions"
REQUIRED_COLUMNS = ['#', 'rerank', 'cosine', 'candidate', 'video_id', 'frame', 'time(s)', 'keyframe_id']

os.makedirs(QUERY_DIR, exist_ok=True)
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# ==============================================================================
# 2. HÀM XỬ LÝ FILE
# ==============================================================================
def parse_query_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '#' in content:
        parts = re.split(r'^\s*#\s+', content, flags=re.MULTILINE)
        description = parts[0].strip()
        table_str = "# " + parts[1].strip() if len(parts) > 1 else ""
    else:
        description = content.strip()
        table_str = ""
        
    return description, table_str

def validate_and_save_csv(uploaded_file, query_id):
    try:
        df = pd.read_csv(uploaded_file)
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return False, f"Thiếu các cột: {', '.join(missing_cols)}", None
        
        if df.empty:
            return False, "File CSV rỗng!", None
        
        save_path = os.path.join(SUBMISSION_DIR, f"{query_id}.csv")
        df.to_csv(save_path, index=False)
        return True, "Upload CSV thành công!", df
    except Exception as e:
        return False, f"Lỗi đọc file CSV: {str(e)}", None

# ==============================================================================
# 3. SIDEBAR: UPLOAD FILE ĐỀ BÀI (.TXT) & CHỌN CÂU HỎI
# ==============================================================================
st.sidebar.title("⚙️ Quản lý Đề Bài")

# --- NÚT UPLOAD ĐỀ BÀI (MỚI BỔ SUNG) ---
with st.sidebar.expander("📤 Nạp/Thêm File Đề Bài (.txt)", expanded=True):
    uploaded_query_files = st.file_uploader(
        "Kéo thả 1 hoặc nhiều file .txt đề bài vào đây:",
        type=["txt"],
        accept_multiple_files=True
    )
    if uploaded_query_files:
        for q_file in uploaded_query_files:
            file_path = os.path.join(QUERY_DIR, q_file.name)
            with open(file_path, "wb") as f:
                f.write(q_file.getbuffer())
        st.success(f"Đã nạp thành công {len(uploaded_query_files)} file đề bài!")
        st.rerun()

st.sidebar.divider()
st.sidebar.header("📋 Danh sách Query")

# Đếm và lấy danh sách file
query_files = sorted([f for f in os.listdir(QUERY_DIR) if f.endswith('.txt')])
total_queries = len(query_files)
submitted_queries = [f.replace('.csv', '') for f in os.listdir(SUBMISSION_DIR) if f.endswith('.csv')]
completed_count = len(submitted_queries)
progress_pct = (completed_count / total_queries) if total_queries > 0 else 0.0

if total_queries == 0:
    st.sidebar.warning("Vui lòng mở mục 'Nạp/Thêm File Đề Bài' ở trên để nạp các file .txt vào hệ thống.")
    selected_query_file = None
else:
    query_options = []
    for qf in query_files:
        qid = qf.replace('.txt', '')
        status_icon = "✅" if qid in submitted_queries else "⏳"
        query_options.append(f"{status_icon} {qid}")
    
    selected_option = st.sidebar.radio("Chọn câu hỏi để làm:", query_options)
    selected_query_id = selected_option.split(" ")[1]
    selected_query_file = f"{selected_query_id}.txt"

# ==============================================================================
# 4. GIAO DIỆN CHÍNH (MAIN DASHBOARD)
# ==============================================================================
st.title("🎯 AI Challenge - Evaluation & Query Submission Dashboard")

# --- THANH TIẾN ĐỘ ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Queries", total_queries)
col2.metric("Completed", completed_count)
col3.metric("Remaining", total_queries - completed_count)

st.progress(progress_pct, text=f"Tiến độ hoàn thành: {completed_count}/{total_queries} ({progress_pct*100:.1f}%)")
st.divider()

# --- CHI TIẾT CÂU HỎI & UPLOAD KẾT QUẢ ---
if selected_query_file:
    st.subheader(f"📌 Đang xem: `{selected_query_id}`")
    
    # Đọc đề bài
    query_txt_path = os.path.join(QUERY_DIR, selected_query_file)
    desc, candidate_table_raw = parse_query_txt(query_txt_path)
    
    with st.expander("📖 Chi tiết Prompt / Visual Description", expanded=True):
        st.markdown(desc)
    
    st.divider()
    
    # Nút Upload CSV kết quả cho câu đang chọn
    st.markdown(f"### 📥 Push File CSV Kết Quả Rerank cho `{selected_query_id}`")
    uploaded_csv = st.file_uploader(
        f"Kéo thả file .csv kết quả vào đây", 
        type=["csv"],
        key=selected_query_id
    )
    
    if uploaded_csv is not None:
        success, msg, df_result = validate_and_save_csv(uploaded_csv, selected_query_id)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    # Hiển thị bảng đã nộp
    submission_file_path = os.path.join(SUBMISSION_DIR, f"{selected_query_id}.csv")
    if os.path.exists(submission_file_path):
        st.markdown("#### 📊 Dữ liệu đã nộp gần nhất:")
        existing_df = pd.read_csv(submission_file_path)
        st.dataframe(existing_df, use_container_width=True)
