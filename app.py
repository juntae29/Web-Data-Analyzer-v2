import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import fitz  # PyMuPDF (PDF 파일 분석용)
from collections import Counter

# 외부 모듈 연동 (동일 폴더 내의 scraper.py 및 analyzer.py)
from scraper import run_web_scraper
import analyzer

# ----------------------------------------------------------------
# 1. 웹 페이지 기본 레이아웃 및 제목 설정
# ----------------------------------------------------------------
st.set_page_config(page_title="Web Data Scraping & Analysis System", layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.markdown("This system executes advanced text mining analytics from academic web sources, PDF documents, and custom inputs.")

# ----------------------------------------------------------------
# [UI 최종 해결] 전역 위젯 및 하단 단축키 문구 초강력 시인성 강화 CSS
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 입력 상자 안에 실제 작성되는 글자 크기 및 색상 조정 */
    .stTextArea textarea {
        font-size: 18px !important;
        color: #111111 !important;
        line-height: 1.6 !important;
    }
    
    /* 입력 상자 내부의 플레이스홀더(안내 문구) 글자 크기 및 선명도 강화 */
    .stTextArea textarea::placeholder {
        font-size: 16px !important;
        color: #444444 !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }
    
    /* [완벽 해결] 오른쪽 아래 'Press Ctrl+Enter to apply' 안내문구 크기 및 색상 강제 지정 */
    /* 클래스 노드를 전역적으로 탐색하여 투명도를 없애고 순수 검은색 볼드로 출력함 */
    div[data-testid="stWidgetInstructions"], 
    div[data-testid="stWidgetInstructions"] span, 
    div[data-testid="stWidgetInstructions"] small,
    .stTextArea div legend + div {
        font-size: 16px !important;        /* 글자 크기를 크게 변경 */
        color: #000000 !important;        /* 완벽한 순수 검은색 전환 */
        font-weight: 900 !important;        /* 가장 두꺼운 폰트 웨이트 부여 */
        opacity: 1 !important;             /* 반투명 마스킹 해제 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ----------------------------------------------------------------
# 2. 사이드바 글로벌 컨트롤 패널 구성 (3가지 분석 모드)
# ----------------------------------------------------------------
st.sidebar.header("⚙️ Global Control Panel")
analysis_mode = st.sidebar.selectbox(
    "Select Analysis Mode",
    ["arXiv Web Scraping", "PDF Document Analysis", "Direct Text Input"]
)

# 데이터 처리를 위한 공통 타겟 변수 초기화
word_df = None
filtered_words = None
csv_file = "scraped_data.csv"
show_raw_df = False

# [모드 1] arXiv 웹 크롤러 엔진 작동 모드
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
                st.rerun()
            else:
                st.sidebar.error("Extraction process failed. Please check connection.")

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        st.subheader(f"📋 Dataset Overview (Total Records Fetched: {len(df)})")
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
                st.error(f"Java Engine (KoNLPy) JVM Connection Required. Details: {e}")

# ----------------------------------------------------------------
# 3. 공통 대시보드 시각화 레이아웃 레이어 (데이터가 준비되었을 때만 출력)
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
                # OSError 발생을 방지하기 위해 font_path 설정을 과감히 생략하고 내장 폰트 엔진 활용
                wordcloud = analyzer.generate_wordcloud_obj(filtered_words, font_path=None)
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