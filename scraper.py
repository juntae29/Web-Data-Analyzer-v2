import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def run_web_scraper(search_query="Artificial Intelligence", num_papers=30):
    print(f"[{search_query}] 데이터 수집 엔진 가동 중이다...")
    
    url = f"https://arxiv.org/search/?query={search_query.replace(' ', '+')}&searchtype=all&source=header"
    headers = {
        "User-Agent": "Professional-Data-Scraper-Bot (bkbcoffice1004@gmail.com)"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("대상 사이트 접근에 실패했다.")
        return False
        
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("li", class_="arxiv-result")
    
    extracted_records = []
    
    for article in articles[:num_papers]:
        title_el = article.find("p", class_="title")
        summary_el = article.find("p", class_="abstract")
        date_el = article.find("p", class_="is-submitted-by")
        
        if title_el and summary_el:
            title = re.sub(r'\s+', ' ', title_el.text.strip())
            summary = re.sub(r'\s+', ' ', summary_el.text.replace("Abstract:", "").strip())
            
            date_text = date_el.text if date_el else ""
            year_match = re.search(r'(19|20)\d{2}', date_text)
            year = year_match.group() if year_match else "2026"
            
            extracted_records.append({
                "Title": title,
                "Summary": summary,
                "Year": year
            })
        time.sleep(0.1)
        
    df = pd.DataFrame(extracted_records)
    output_filename = "scraped_data.csv"
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"성공적으로 {len(df)}건의 데이터를 파싱하여 '{output_filename}'에 저장했다.")
    return True

if __name__ == "__main__":
    run_web_scraper()