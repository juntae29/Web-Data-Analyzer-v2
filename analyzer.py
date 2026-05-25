import re
from konlpy.tag import Okt
from wordcloud import WordCloud
import pandas as pd
import os
import platform

def process_korean_text(text):
    """
    입력된 텍스트에서 한글 형태소 분석을 통해 명사만 추출하는 함수
    """
    if not text or not isinstance(text, str):
        return []
    
    okt = Okt()
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
    [핵심 수정] 한글 깨짐 현상을 근본적으로 해결하기 위해 폰트 경로를 완벽하게 바인딩하는 함수
    """
    # 1. 호출부에서 폰트 경로를 주지 않았거나 누락된 경우, OS별 표준 폰트 자동 추적
    if not font_path:
        if platform.system() == "Windows":
            font_path = "C:\\Windows\\Fonts\\malgun.ttf"
        elif platform.system() == "Darwin":
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
            
    # 2. 지정된 폰트 파일이 실제로 존재하는지 최종 검증 (존재하지 않으면 굴림체로 우회)
    if font_path and not os.path.exists(font_path):
        if platform.system() == "Windows":
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        else:
            font_path = None

    # 리스트 형태의 형태소를 하나의 문자열 스페이스 단위로 결합
    text_content = " ".join(text_list)
    
    # 3. WordCloud 객체 생성 시 font_path를 강제로 주입하여 한글 매핑 완료
    wc = WordCloud(
        font_path=font_path,
        width=800,
        height=500,
        background_color="white",
        colormap="plasma",
        prefer_horizontal=0.9
    )
    
    return wc.generate(text_content)