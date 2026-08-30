import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 1. CAU HINH TRANH NGHEN PAGE & TRANG THAI GIAO DIEN
# ==============================================================================
st.set_page_config(page_title="AI Challenge Query Manager", layout="wide")

QUERY_DIR = "data/queries"
SUBMISSION_DIR = "data/submissions"
REQUIRED_COLUMNS = ['#', 'rerank', 'cosine', 'candidate', 'video_id', 'frame', 'time(s)', 'keyframe_id']

os.makedirs(QUERY_DIR, exist_ok=True)
os.makedirs(SUBMISSION_DIR, exist_ok=True)

# ==============================================================================
# 2. HAM XU LY FILE QUERY (.TXT) VA FILE KET QUA (.CSV)
# ==============================================================================
def parse_query_txt(file_path):
    """
    Đọc file query-p1-xx.txt để tách phần Mô tả (Prompt) và Bảng Candidate gốc (nếu có)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tách đoạn text mô tả và phần bảng dữ liệu dựa vào dòng tiêu đề bảng '#'
    if '#' in content:
        parts = re.split(r'^\s*#\s+', content, flags=re.MULTILINE)
        description = parts[0].strip()
        table_str = "# " + parts[1].strip() if len(parts) > 1 else ""
    else:
        description = content.strip()
        table_str = ""
        
    return description, table_str

def validate_and_save_csv(uploaded_file, query_id):
    """
    Validate định dạng file CSV tải lên và lưu trữ nếu hợp lệ
    """
    try:
        df = pd.read_csv(uploaded_file)
        
        # 1. Kiểm tra cột bắt buộc
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return False, f"Thiếu các cột: {', '.join(missing_cols)}", None
        
        # 2. Kiểm tra dữ liệu rỗng
        if df.empty:
            return False, "File CSV rỗng!", None
        
        # 3. Lưu file vào thư mục submissions
        save_path = os.path.join(SUBMISSION_DIR, f"{query_id}.csv")
        df.to_csv(save_path, index=False)
        
        return True, "Upload thành công và đã cập nhật tiến độ!", df

    except Exception as e:
        return False, f"Lỗi đọc file CSV: {str(e)}", None

# ==============================================================================
# 3. QUAN LY TIEN DO (PROGRESS TRACKER)
# ==============================================================================
# Lấy danh sách tất cả các câu truy vấn từ thư mục data/queries
query_files = sorted([f for f in os.listdir(QUERY_DIR) if f.endswith('.txt')])
total_queries = len(query_files)

# Đếm số câu đã nộp (dựa trên các file CSV tồn tại trong SUBMISSION_DIR)
submitted_queries = [f.replace('.csv', '') for f in os.listdir(SUBMISSION_DIR) if f.endswith('.csv')]
completed_count = len(submitted_queries)
progress_pct = (completed_count / total_queries) if total_queries > 0 else 0.0

# ==============================================================================
# 4. GIAO DIEN MAIN DASHBOARD
# ==============================================================================
st.title("🎯 AI Challenge - Evaluation & Query Submission Dashboard")

# --- KHU VUC 1: THANH TIEN DO (METRICS & PROGRESS BAR) ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Queries", total_queries)
col2.metric("Completed", completed_count)
col3.metric("Remaining", total_queries - completed_count)

st.progress(progress_pct, text=f"Tiến độ hoàn thành: {completed_count}/{total_queries} ({progress_pct*100:.1f}%)")
st.divider()

# --- KHU VUC 2: SIDEBAR CHON CAU TRUY VAN ---
st.sidebar.header("📋 Danh sách Query")
if total_queries == 0:
    st.sidebar.warning(f"Chưa có file query nào trong `{QUERY_DIR}`")
    selected_query_file = None
else:
    # Đánh dấu icon cho câu đã nộp / chưa nộp
    query_options = []
    for qf in query_files:
        qid = qf.replace('.txt', '')
        status_icon = "✅" if qid in submitted_queries else "⏳"
        query_options.append(f"{status_icon} {qid}")
    
    selected_option = st.sidebar.radio("Chọn câu hỏi:", query_options)
    selected_query_id = selected_option.split(" ")[1]
    selected_query_file = f"{selected_query_id}.txt"

# --- KHU VUC 3: CHI TIET CAU HOI & UPLOAD ---
if selected_query_file:
    st.subheader(f"📌 Đang xem: `{selected_query_id}`")
    
    # Đọc thông tin đề bài từ file txt[cite: 1]
    query_txt_path = os.path.join(QUERY_DIR, selected_query_file)
    desc, candidate_table_raw = parse_query_txt(query_txt_path)
    
    # Hiển thị mô tả đề bài
    with st.expander("📖 Chi tiết Prompt / Visual Description", expanded=True):
        st.markdown(desc)
    
    st.divider()
    
    # Khu vực Upload file CSV kết quả
    st.markdown("### 📥 Push File CSV Kết Quả Rerank")
    uploaded_csv = st.file_uploader(
        f"Kéo thả file .csv kết quả cho `{selected_query_id}` vào đây", 
        type=["csv"],
        key=selected_query_id
    )
    
    if uploaded_csv is not None:
        success, msg, df_result = validate_and_save_csv(uploaded_csv, selected_query_id)
        if success:
            st.success(msg)
            st.rerun() # Refresh lại để cập nhật progress bar ngay lập tức
        else:
            st.error(msg)

    # Hiển thị kết quả đã nộp (nếu đã có trong SUBMISSION_DIR)
    submission_file_path = os.path.join(SUBMISSION_DIR, f"{selected_query_id}.csv")
    if os.path.exists(submission_file_path):
        st.markdown("#### 📊 Dữ liệu đã nộp gần nhất:")
        existing_df = pd.read_csv(submission_file_path)
        st.dataframe(existing_df, use_container_width=True)
