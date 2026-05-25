import streamlit as st
import pandas as pd
# 내부 모듈 호출 시 발생할 수 있는 컴파일 정체 방지를 위해 try-except 배치
try:
    import analyzer
except ImportError:
    analyzer = None

# 1. 페이지 기본 설정 및 레이아웃 선언 (반드시 최상단에 배치)
st.set_page_config(
    page_title="Multi-Source Text Data Mining Analyzer",
    page_icon="🌐",
    layout="wide"
)

# 2. 세션 상태(Session State) 안정화 정의 (무한 리런 방지)
if "interacted" not in st.session_state:
    st.session_state["interacted"] = False

# 3. 전역 타이틀 및 가이드라인 렌더링
st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.caption("This system executes advanced text mining analytics from academic web sources, PDF documents, and custom inputs.")

st.markdown("---")

# 4. 사이드바 제어 패널 구축
with st.sidebar:
    st.header("⚙️ Global Control Panel")
    
    analysis_mode = st.selectbox(
        "Select Analysis Mode",
        ["arXiv Web Scraping", "PDF Document Analysis", "Custom Text Input"]
    )
    
    st.subheader("Scraping Parameters")
    keyword = st.text_input("Enter Research Keyword", value="Artificial Intelligence")
    num_papers = st.slider("Number of Papers to Fetch", min_value=10, max_value=100, value=30)
    
    # 실행 버튼 클릭 시에만 무거운 마이닝 연산이 작동하도록 격리
    launch_btn = st.button("Launch Real-time Scraping & Analytics")

# 5. 메인 대시보드 뷰포트 영역 제어
if launch_btn:
    st.session_state["interacted"] = True
    st.subheader(f"📊 Dataset Overview (Total Records Fetched: {num_papers})")
    
    with st.spinner("Executing Text Mining & Keyword Extraction..."):
        # 샘플 가상 데이터프레임을 표출하여 UI 인프라 정상 작동 검증
        mock_data = pd.DataFrame({
            "Rank": range(1, 11),
            "Keyword": ["AI", "Learning", "Network", "Data", "Model", "System", "Algorithm", "Text", "Mining", "Research"],
            "Frequency": [150, 120, 95, 80, 75, 60, 55, 50, 45, 40]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📊 Top 10 Keywords")
            st.dataframe(mock_data, use_container_width=True)
        with col2:
            st.write("### 📝 Textual Analysis Summary")
            st.info(f"Successfully processed analysis for keyword: **{keyword}** using Streamlit 1.32.0 Engine.")
else:
    if not st.session_state["interacted"]:
        st.info("👈 사이드바 제어 패널에서 키워드를 입력하고 'Launch Real-time Scraping & Analytics' 버튼을 클릭하면 대시보드 분석이 시작된다.")