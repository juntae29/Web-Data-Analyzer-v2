import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import fitz  # PyMuPDF
import platform
from collections import Counter

# 외부 모듈 연동
from scraper import run_web_scraper
import analyzer

# ----------------------------------------------------------------
# [폰트 해결] 클라우드 리눅스 서버 환경 반영 표준 폰트 설정
# ----------------------------------------------------------------
font_name = None
if platform.system() == "Windows":
    font_name = "C:\\Windows\\Fonts\\malgun.ttf"
    if not os.path.exists(font_name):
        font_name = "C:\\Windows\\Fonts\\gulim.ttc"
elif platform.system() == "Darwin":
    font_name = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
elif platform.system() == "Linux":
    linux_fonts = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
        "/usr/share/fonts/truetype/nanum/NanumSquareR.ttf",
        "/usr/share/fonts/fonts-nanum/NanumGothic.ttf"
    ]
    for path in linux_fonts:
        if os.path.exists(path):
            font_name = path
            break

if font_name and not os.path.exists(font_name):
    font_name = None

# ----------------------------------------------------------------
# 웹 페이지 기본 레이아웃 및 제목 설정
# ----------------------------------------------------------------
st.set_page_config(page_title="Web Data Scraping & Analysis System", layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.markdown("This system executes advanced text mining analytics from academic web sources, PDF documents, and custom inputs.")

# ----------------------------------------------------------------
# 세션 상태 및 인프라 보호용 트리거 초기화
# ----------------------------------------------------------------
if "scraping_done" not in st.session_state:
    st.session_state.scraping_done = False

# 위젯 지침 및 텍스트 영역 스타일 제어 CSS Layer
st.markdown(
    """
    <style>
    .stTextArea textarea {
        font-size: 18px !important;
        color: #111111 !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea::placeholder {
        font-size: 16px !important;
        color: #444444 !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    div[data-testid="stWidgetInstructions"], 
    div[data-testid="stWidgetInstructions"] span, 
    div[data-testid="stWidgetInstructions"] small,
    .stTextArea div legend + div {
        font-size: 16px !important;        
        color: #000000 !important;        
        font-weight: 900 !important;        
        opacity: 1 !important;             
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ----------------------------------------------------------------
# 사이드바 글로벌 컨트롤 패널 구성
# ----------------------------------------------------------------
st.sidebar.header("⚙️ Global Control Panel")
analysis_mode = st.sidebar.selectbox(
    "Select Analysis Mode",
    ["arXiv Web Scraping", "PDF Document Analysis", "Direct Text Input"]
)

word_df = None
filtered_words = None
csv_file = "scraped_data.csv"
show_raw_df = False

# [모드 1] arXiv 웹 크롤러 엔진 작동 모드 (세션 보호 레이어 적용)
if analysis_mode == "arXiv Web Scraping":
    st.sidebar.subheader("Scraping Parameters")
    search_topic = st.sidebar.text_input("Enter Research Keyword", value="Artificial Intelligence")
    paper_count = st.sidebar.slider("Number of Papers to Fetch", min_value=10, max_value=50, value=30)
    start_scraping = st.sidebar.button("Launch Real-time Scraping & Analytics")

    if start_scraping:
        with st.spinner("Accessing target database and extracting textual datasets..."):
            success = run_web_scraper(search_query=search_topic, num_papers=paper_count)
            if success:
                st.sidebar.success("Data extraction completed and saved to CSV!")
                st.session_state.scraping_done = True
                st.rerun()
            else:
                st.sidebar.error("Extraction process failed. Please check connection.")

    # 전역 공간 무한 로딩 차단: 사용자가 버튼을 눌렀거나, 세션 스테이트가 활성화되었을 때만 마이닝 연산 작동
    if st.session_state.scraping_done and os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.subheader(f"📋 Dataset Overview (Total Records Fetched: {len(df)})")
        with st.spinner("Running text mining algorithms..."):
            word_df, filtered_words = analyzer.process_dataframe_mining(df)
        show_raw_df = True
    else:
        st.info("Please trigger the scraping engine from the sidebar panel to render the analytical dashboards.")

# [모드 2] PDF 파일 분석 모드
elif analysis_mode == "PDF Document Analysis":
    st.subheader("📁 PDF Document Core Word Analysis")
    uploaded_file = st.file_uploader("Upload a PDF file to parse text structures", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Extracting strings from PDF file container..."):
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                raw_text = " ".join([page.get_text() for page in doc])
                filtered_words = analyzer.process_korean_text(raw_text)
                if filtered_words:
                    word_counts = Counter(filtered_words)
                    word_df = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"])
                    st.success(f"Successfully processed PDF file ({len(doc)} pages extracted).")
                else:
                    st.warning("No significant dynamic words could be extracted from the PDF file.")
            except Exception as e:
                st.error(f"PDF Analysis Crash Info: {e}")

# [모드 3] 텍스트 상자 입력 분석 모드
elif analysis_mode == "Direct Text Input":
    st.subheader("📝 Text Container Data Mining")
    user_input = st.text_area("Paste or enter your target paragraph here", height=250,
                             placeholder="Enter text strings here to analyze frequent core entities...")
    
    if user_input.strip():
        with st.spinner("Analyzing input text block..."):
            try:
                filtered_words = analyzer.process_korean_text(user_input)
                if filtered_words:
                    word_counts = Counter(filtered_words)
                    word_df = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"])
                else:
                    st.warning("No significant dynamic nouns found in the text container.")
            except Exception as e:
                st.error(f"Analysis Processing Error. Details: {e}")

# ----------------------------------------------------------------
# 공통 대시보드 시각화 레이아웃 레이어
# ----------------------------------------------------------------
if word_df is not None and not word_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Core Keyword Frequencies")
        st.bar_chart(data=word_df.set_index("Word"))
        
    with col2:
        st.subheader("📝 Textual Analysis Word Cloud")
        if filtered_words:
            try:
                wordcloud = analyzer.generate_wordcloud_obj(filtered_words, font_path=font_name)
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            except Exception as e:
                st.error(f"WordCloud Render Error: {e}")
        else:
            st.info("No words available to generate cloud visual.")
            
    if show_raw_df:
        st.markdown("---")
        st.subheader("🔍 Scraped Raw Metadata Dataframe")
        st.dataframe(df, use_container_width=True)