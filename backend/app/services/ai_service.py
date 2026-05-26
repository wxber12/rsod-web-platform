# 建议在 app/services/ai_service.py 中实现
import httpx
from app.config import settings


async def chat_with_deepseek(question: str, history: list = None):
    if not settings.DEEPSEEK_API_KEY:
        return "DeepSeek API Key 未配置，无法提供 AI 服务。"

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    payload = {
        "model": "deepseek-chat",
        "messages": messages
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            return f"AI 服务响应错误: {e.response.status_code}"
        except Exception as e:
            return f"AI 服务请求失败: {str(e)}"