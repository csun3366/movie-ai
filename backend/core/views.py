import json
import os
import openai
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

from .crawler import fetch_ptt_movie_articles

openrouter_key = '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'

def chat_with_openrouter(messages, model="deepseek/deepseek-r1:free"):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "my ai app"
    }

    data = {
        "model": model,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def home(request):
    return render(request, 'home.html')

@csrf_exempt
def summarize_review(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    try:
        data = json.loads(request.body)
        movie_name = data.get('movie_name')

        articles = fetch_ptt_movie_articles(movie_name)
        if not articles:
            return JsonResponse({'summary': "無法取得相關文章"})
        # 整理評論文字
        prompt = f"請根據收集到的 Google 評論，幫我總結「{movie_name}」的評價，幫我分別整理出這部電影在 主題與劇情 角色與表演 情感共鳴 導演風格與敘事手法 攝影與美術設計 音效與配樂 剪輯與節奏 方面的優點與缺點，每項都要列出具體事例或說法，要用繁體中文評論，格式要是:💡 主題與劇情，🎭 角色與表演， ❤️情感共鳴，🎥 導演風格與敘事手法，📷 攝影與美術設計，🎼 音效與配樂，✏️ 剪輯與節奏，優缺點也以以下格式呈現:✅優點 ❌ 缺點，請不要使用 ** 或 Markdown 粗體符號，直接用純文字輸出分類標題與說明\n\n"
        for article in articles:
            prompt += f"- {article}\n"

        # 步驟 3: 傳送給 OpenAI 進行摘要
        messages=[
            {"role": "system", "content": "你是一個中文評論分析專家"},
            {"role": "user", "content": prompt}
        ]
        reply = chat_with_openrouter(messages)
        print("AI 回答：", reply)
        return JsonResponse({'summary': reply})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
