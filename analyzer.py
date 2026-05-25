import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import os
import platform

# 1. 영문 데이터 분석 및 정제 (기존 로직 유지)
def process_english_text(text):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower()) 
    stopwords = {"with", "from", "that", "this", "these", "those", "their", "which", "about", "using", "based", "abstract"}
    filtered_words = [word for word in words if word not in stopwords]
    return filtered_words

# 2. [자바 프리] 한국어 및 혼합 텍스트 정제 알고리즘
def process_korean_text(text):
    # 자바가 필요한 KoNLPy 대신, 정규표현식을 사용하여 한글/영문 단어(2글자 이상)를 직접 추출한다.
    # 한글([가-힣]) 또는 영문([a-zA-Z]) 단어를 찾아낸다.
    words = re.findall(r'\b[가-힣a-zA-Z]{2,}\b', text)
    
    # 한국어/영어 통합 불용어 사전을 구성하여 의미 없는 단어를 필터링한다.
    stopwords = {
        "이것", "그것", "저것", "정말", "진짜", "의한", "위한", "통해", "대해", "설정", 
        "수정", "마치", "이후", "다시", "아래", "기존", "파일", "코드", "화면", "하기",
        "with", "from", "that", "this", "these", "those", "about", "using"
    }
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return filtered_words

# 3. 데이터프레임 기반 텍스트 마이닝 (arXiv 웹용)
def process_dataframe_mining(df):
    if df is None or df.empty:
        return None, None
    all_text = " ".join(df["Title"].dropna()) + " " + " ".join(df["Summary"].dropna())
    filtered_words = process_english_text(all_text)
    
    word_counts = Counter(filtered_words)
    top_words = word_counts.most_common(10)
    word_df = pd.DataFrame(top_words, columns=["Word", "Count"])
    return word_df, filtered_words

# 4. 워드클라우드 객체 생성 공통 함수
def generate_wordcloud_obj(filtered_words, font_path=None):
    combined_text = " ".join(filtered_words)
    wordcloud = WordCloud(
        font_path=font_path,
        width=600, 
        height=400, 
        background_color="white", 
        colormap="plasma"
    ).generate(combined_text)
    return wordcloud

# 단독 실행 모드 지원 로직
def analyze_collected_data(csv_file="scraped_data.csv"):
    if not os.path.exists(csv_file):
        print(f"오류: '{csv_file}' 데이터 파일이 존재하지 않는다. scraper.py를 먼저 실행하라.")
        return

    df = pd.read_csv(csv_file)
    print(f"\n--- 데이터 통계 정밀 분석 시작 (총 {len(df)}건 레코드 수집됨) ---")

    word_df, filtered_words = process_dataframe_mining(df)
    if word_df is None:
        print("분석할 텍스트가 존재하지 않는다.")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    ax1.barh(word_df["Word"], word_df["Count"], color="teal")
    ax1.invert_yaxis()
    ax1.set_title("Top 10 Frequent Keywords")
    
    local_font = None
    if platform.system() == "Windows":
        local_font = "C:\\Windows\\Fonts\\malgun.ttf"
    elif platform.system() == "Darwin":
        local_font = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"

    wordcloud = generate_wordcloud_obj(filtered_words, font_path=local_font)
    ax2.imshow(wordcloud, interpolation="bilinear")
    ax2.axis("off")
    ax2.set_title("Research Text Word Cloud")
    
    plt.tight_layout()
    report_output = "analysis_report.png"
    plt.savefig(report_output, dpi=300)
    print(f"고해상도 시각화 분석 리포트가 '{report_output}' 파일로 안전하게 저장되었다.")
    plt.show()

if __name__ == "__main__":
    analyze_collected_data()