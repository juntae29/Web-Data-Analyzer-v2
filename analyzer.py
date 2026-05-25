import re
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import pandas as pd
import os
import platform

# 순수 파이썬 기반 Kiwi 형태소 분석기 전역 인스턴스
_kiwi_instance = None

def get_kiwi():
    global _kiwi_instance
    if _kiwi_instance is None:
        _kiwi_instance = Kiwi()
    return _kiwi_instance

def process_korean_text(text):
    """
    입력된 텍스트에서 한글 명사 및 영문 핵심 키워드를 추출하고 불용어를 제거하는 함수
    """
    if not text or not isinstance(text, str):
        return []
    
    kiwi = get_kiwi()
    
    # 특수문자 정제 (한글, 영문, 공백 유지)
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', text)
    
    # Kiwi 토큰화 진행
    tokens = kiwi.tokenize(clean_text)
    
    # NNG(일반명사), NNP(고유명사) 외에 영문 키워드 처리를 위해 SL(외국어) 태그 추가 반영
    allowed_tags = ['NNG', 'NNP', 'SL']
    
    # 해당 태그에 속하는 단어만 추출하되, 영어는 분석 일관성을 위해 소문자로 통일
    raw_words = []
    for t in tokens:
        if t.tag in allowed_tags:
            word = t.form.lower() if t.tag == 'SL' else t.form
            raw_words.append(word)
    
    # 한영 통합 맞춤형 불용어 사전 세분화
    stop_words = [
        '그것', '이것', '저것', '때문', '위해', '대한', '통해', '관한',
        '다함께', '우리', '우리의', '무리를', '함께', '모든', '통하여', 
        '대하여', '있습니다', '아래', '이상', '이하', '내용', '구분',
        'the', 'and', 'of', 'to', 'in', 'is', 'for', 'that', 'with', 'on', 'as', 'by', 'an', 'this', 'we'
    ]
    
    # 2글자 이상이면서 불용어 사전에 포함되지 않은 단어만 최종 필터링
    filtered_nouns = [word for word in raw_words if len(word) > 1 and word not in stop_words]
    
    return filtered_nouns

def process_dataframe_mining(df):
    """
    데이터프레임 기반 텍스트 데이터 파싱 함수 (Abstract 또는 title 우선 매핑)
    """
    if 'Abstract' in df.columns:
        all_text = " ".join(df['Abstract'].fillna("").astype(str).tolist())
    elif 'title' in df.columns:
        all_text = " ".join(df['title'].fillna("").astype(str).tolist())
    else:
        all_text = ""
        
    filtered_words = process_korean_text(all_text)
    
    if filtered_words:
        from collections import Counter
        word_counts = Counter(filtered_words)
        word_df = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"])
        return word_df, filtered_words
    else:
        return pd.DataFrame(columns=["Word", "Count"]), []

def generate_wordcloud_obj(text_list, font_path=None):
    """
    Streamlit Cloud(Linux) 환경에서 한글 깨짐 네모 현상을 완벽하게 해결하는 폰트 매핑 함수
    """
    if not font_path:
        sys_plat = platform.system()
        if sys_plat == "Windows":
            font_path = "C:\\Windows\\Fonts\\malgun.ttf"
        elif sys_plat == "Darwin":
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        elif sys_plat == "Linux":
            # 데비안/우분투 계열 리눅스의 다양한 나눔폰트 경로 배열 탐색
            linux_fonts = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf",
                "/usr/share/fonts/truetype/nanum/NanumSquareR.ttf",
                "/usr/share/fonts/fonts-nanum/NanumGothic.ttf"
            ]
            for path in linux_fonts:
                if os.path.exists(path):
                    font_path = path
                    break
            else:
                font_path = None
                
    # fallback 폰트 처리 (Windows 기본 폰트 대비)
    if font_path and not os.path.exists(font_path):
        if platform.system() == "Windows":
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        else:
            font_path = None

    text_content = " ".join(text_list)
    
    # 한글 및 영문 공용 워드클라우드 객체 선언
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=500,
        background_color="white",
        colormap="plasma",
        prefer_horizontal=0.9
    )
    
    return wc.generate(text_content)