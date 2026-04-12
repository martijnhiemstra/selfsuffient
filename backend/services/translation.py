"""Translation service using OpenAI API."""
import json
import httpx
from typing import Dict

SUPPORTED_LANGUAGES = {
    "en": "English",
    "nl": "Dutch",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "it": "Italian",
    "pl": "Polish",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "ro": "Romanian",
    "hu": "Hungarian",
    "el": "Greek",
    "tr": "Turkish",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ru": "Russian",
    "uk": "Ukrainian",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
}


async def translate_content(
    api_key: str,
    model: str,
    title: str,
    content: str,
    source_lang: str,
    target_lang: str,
) -> Dict[str, str]:
    """Translate title and content using OpenAI."""
    source_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
    target_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)

    system_prompt = (
        f"You are a professional translator. Translate the following from {source_name} to {target_name}. "
        "Preserve all HTML formatting tags exactly as they are. Only translate the text content. "
        "Return JSON with keys 'title' and 'content' containing the translated text."
    )

    user_prompt = json.dumps({"title": title, "content": content}, ensure_ascii=False)

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
        )

        if response.status_code == 401:
            raise ValueError("Invalid OpenAI API key")
        if response.status_code == 429:
            raise ValueError("OpenAI rate limit exceeded. Try again later.")
        if response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.status_code}")

        result = response.json()
        text = result["choices"][0]["message"]["content"]
        parsed = json.loads(text)

        return {
            "title": parsed.get("title", title),
            "content": parsed.get("content", content),
        }
