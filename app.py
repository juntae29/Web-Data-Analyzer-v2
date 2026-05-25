import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import fitz  # PyMuPDF (PDF 파일 분석용)
import platform
from collections import Counter

# 외부 모듈 연동 (동일 폴더 내의 scraper.py 및 analyzer.py)
from scraper import run_web_scraper
import analyzer

# ----------------------------------------------------------------
# 1. 시스템 환경별 맑은 고딕 / 애플고딕 폰트 절대 경로 설정 (OSError 방지)
# ----------------------------------------------------------------
if platform.system() == "Windows":
    font_name = "C:\\Windows\\Fonts\\malgun.ttf"
elif platform.system() == "Darwin":
    font_name = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
else:
    font_name = None

# ----------------------------------------------------------------
# 2. 웹 페이지 기본 레이아웃 및 제목 설정
# ----------------------------------------------------------------
st.set_page_config(page_title="Web Data Scraping & Analysis System", layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.markdown("This system executes advanced text mining analytics from academic web sources, PDF documents, and custom inputs.")
st.markdown("---")

# ----------------------------------------------------------------
# 3. 사이드바 글로벌 컨트롤 패널 구성 (3가지 분석 모드)
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

# [모드 1] 기존의 arXiv 웹 크롤러 엔진 작동 모드
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
        
        # analyzer.py 모듈을 이용하여 영문 텍스트 데이터프레임 기반 파싱 진행
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
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            raw_text = " ".join([page.get_text() for page in doc])
            
            # KoNLPy 및 정형화 필터링을 거쳐 명사 리스트 추출
            filtered_words = analyzer.process_korean_text(raw_text)
            if filtered_words:
                word_counts = Counter(filtered_words)
                word_df = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"])
                st.success(f"Successfully processed PDF file ({len(doc)} pages extracted).")
            else:
                st.warning("No significant dynamic words could be extracted from the PDF file.")

# [모드 3] 텍스트 상자 입력 분석 모드
elif analysis_mode == "Direct Text Input":
    st.subheader("📝 Text Container Data Mining")
    user_input = st.text_area("Paste or enter your target paragraph here", height=250,
                             placeholder="Enter text strings here to analyze frequent core entities...")
    
    if user_input.strip():
        with st.spinner("Analyzing input text block..."):
            filtered_words = analyzer.process_korean_text(user_input)
            if filtered_words:
                word_counts = Counter(filtered_words)
                word_df = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"])
            else:
                st.warning("No significant dynamic nouns found in the text container.")

# ----------------------------------------------------------------
# 4. 공통 대시보드 시각화 레이아웃 레이어 (데이터가 준비되었을 때만 출력)
# ----------------------------------------------------------------
if word_df is not None and not word_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Core Keyword Frequencies")
        # 가로형 막대 차트 연동을 위해 인덱스 세팅 후 바 플롯 표출
        st.bar_chart(data=word_df.set_index("Word"))
        
    with col2:
        st.subheader("📝 Textual Analysis Word Cloud")
        if filtered_words:
            # 안전한 절대 경로 시스템 폰트가 담긴 font_name 변수 주입
            wordcloud = analyzer.generate_wordcloud_obj(filtered_words, font_path=font_name)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No words available to generate cloud visual.")
            
    # arXiv 웹 스크래핑 모드일 때만 하단에 수집된 CSV 원본 테이블 표출
    if show_raw_df:
        st.markdown("---")
        st.subheader("🔍 Scraped Raw Metadata Dataframe")
        st.dataframe(df, use_container_width=True)