import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def run_web_scraper(search_query="Artificial Intelligence", num_papers=30):
    print(f"[{search_query}] 데이터 수집 엔진 가동 중이다...")
    
    extracted_records = []
    start_index = 0
    papers_per_page = 50  # arXiv 검색 결과 페이지당 기본 노출 수
    
    headers = {
        "User-Agent": "Professional-Data-Scraper-Bot (bkbcoffice1004@gmail.com)"
    }
    
    # 요청된 num_papers 수량을 채울 때까지 페이지네이션 반복 순회
    while len(extracted_records) < num_papers:
        # start 매개변수를 추가하여 다음 페이지 데이터 추적
        url = f"https://arxiv.org/search/?query={search_query.replace(' ', '+')}&searchtype=all&source=header&size={papers_per_page}&start={start_index}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"대상 사이트 접근에 실패했다. 상태 코드: {response.status_code}")
                break
        except Exception as e:
            print(f"네트워크 요청 중 예외 발생: {e}")
            break
            
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li", class_="arxiv-result")
        
        # 더 이상 검색 결과 항목이 없으면 루프 탈출
        if not articles:
            break
            
        for article in articles:
            if len(extracted_records) >= num_papers:
                break
                
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
                    "title": title,
                    "Abstract": summary,
                    "Year": year
                })
        
        # 다음 페이지 조회를 위한 인덱스 오프셋 증가
        start_index += papers_per_page
        time.sleep(0.5)  # 디도스 방지 및 안정적인 커넥션을 위한 대기 시간 조율
        
    if not extracted_records:
        print("파싱된 데이터 기록이 존재하지 않는다.")
        return False

    df = pd.DataFrame(extracted_records)
    output_filename = "scraped_data.csv"
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")
    print(f"성공적으로 {len(df)}건의 데이터를 파싱하여 '{output_filename}'에 저장했다.")
    return True

if __name__ == "__main__":
    run_web_scraper()