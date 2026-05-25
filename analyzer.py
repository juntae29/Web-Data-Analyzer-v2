import re
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import pandas as pd
import os
import platform

_kiwi_instance = None

def get_kiwi():
    global _kiwi_instance
    if _kiwi_instance is None:
        _kiwi_instance = Kiwi()
    return _kiwi_instance

def process_korean_text(text):
    if not text or not isinstance(text, str):
        return []
    
    kiwi = get_kiwi()
    clean_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
    tokens = kiwi.tokenize(clean_text)
    nouns = [t.form for t in tokens if t.tag in ['NNG', 'NNP']]
    
    stop_words = ['그것', '이것', '저것', '때문', '위해', '대한', '통해', '관한']
    filtered_nouns = [word for word in nouns if len(word) > 1 and word not in stop_words]
    
    return filtered_nouns

def process_dataframe_mining(df):
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