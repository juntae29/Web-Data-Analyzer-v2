import re
from konlpy.tag import Okt
from wordcloud import WordCloud
import pandas as pd
import os
import platform

# JVM 중복 로딩 및 메모리 누수 차단을 위한 전역 객체 선언
_okt_instance = None

def get_okt():
    """
    Okt 객체를 단 한 번만 생성하여 메모리 충돌을 방지하는 함수
    """
    global _okt_instance
    if _okt_instance is None:
        _okt_instance = Okt()
    return _okt_instance

def process_korean_text(text):
    """
    입력된 텍스트에서 한글 형태소 분석을 통해 명사만 추출하는 함수
    """
    if not text or not isinstance(text, str):
        return []
    
    okt = get_okt()
    
    # 특수문자 제거 및 한글, 영문, 숫자 구조 유지
    clean_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
    nouns = okt.nouns(clean_text)
    
    # 의미 없는 단어 및 단음절 단어 필터링 (2글자 이상만 유지)
    stop_words = ['그것', '이것', '저것', '때문', '위해', '대한', '통해', '관한']
    filtered_nouns = [word for word in nouns if len(word) > 1 and word not in stop_words]
    
    return filtered_nouns

def process_dataframe_mining(df):
    """
    arXiv 등 데이터프레임 기반 텍스트 데이터 파싱 함수
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
    한글 깨짐 현상을 근본적으로 해결하기 위해 폰트 경로를 완벽하게 바인딩하는 함수
    """
    if not font_path:
        if platform.system() == "Windows":
            font_path = "C:\\Windows\\Fonts\\malgun.ttf"
        elif platform.system() == "Darwin":
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        elif platform.system() == "Linux":
            font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
            
    if font_path and not os.path.exists(font_path):
        if platform.system() == "Windows":
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        else:
            font_path = None

    text_content = " ".join(text_list)
    
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=500,
        background_color="white",
        colormap="plasma",
        prefer_horizontal=0.9
    )
    
    return wc.generate(text_content)