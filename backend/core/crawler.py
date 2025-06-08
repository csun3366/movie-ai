import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'https://www.ptt.cc'
BOARD = 'movie'
MAX_ARTICLES = 30

headers = {
    'User-Agent': 'Mozilla/5.0',
}

cookies = {
    'over18': '1'
}

def get_search_results(page, keyword):
    url = f'{BASE_URL}/bbs/{BOARD}/search?page={page}&q={keyword}'
    res = requests.get(url, headers=headers, cookies=cookies)
    if res.status_code != 200:
        print(f'⚠️ 第 {page} 頁不存在（{res.status_code}）')
        return []
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    for div in soup.select('div.title'):
        a = div.find('a')
        if a:
            title = a.text.strip()
            link = BASE_URL + a['href']
            results.append({'title': title, 'link': link})
    return results

def get_article_content(article_url):
    res = requests.get(article_url, headers=headers, cookies=cookies)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    main_content = soup.find(id='main-content')
    # 移除 meta info 和推文
    for tag in main_content.find_all(['div', 'span'], class_=['article-metaline', 'article-metaline-right', 'push']):
        tag.decompose()
    content_text = main_content.text.strip()
    return content_text

def fetch_ptt_movie_articles(keyword, max_articles=MAX_ARTICLES):
    articles = []
    page = 1
    count = 0
    while count < max_articles:
        results = get_search_results(page, keyword)
        if not results:
            break
        for res in results:
            if count >= max_articles:
                break
            try:
                content = get_article_content(res['link'])
                articles.append({'title': res['title'], 'link': res['link'], 'content': content})
                count += 1
                # 適時印出
                print(f"\n[{count}] {res['title']}")
                print(f"文章網址: {res['link']}")
                print(f"內容摘錄:\n{content[:300]}...\n{'-'*50}")
                time.sleep(0.5)
            except Exception as e:
                print(f"抓取文章失敗: {res['link']}，原因: {e}")
        page += 1
    return articles