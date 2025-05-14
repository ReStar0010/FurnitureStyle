import sys, json, base64
import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def classify_furniture_from_image(image_path, color_mode: str = "original"):
    """
    傳入一張本機圖片檔路徑，呼叫 GPT-4o 幫你回傳：
      {"種類":"沙發","風格":"北歐風"}
    """
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"告訴我裡面的家具種類和風格（請在 style 裡同時描述風格與主要色調）是什麼？"
                                "請以「{color_mode}」的色彩方式轉換你看到的家具色調"
                                "不要多任何額外文字。也不要回傳markdown格式。"
                                "然後**只**回傳一個 JSON 物件，包含兩個 key：\n"
                                "請**只回傳 JSON**格式，像這樣："
                                "{\"type\":\"沙發\",\"style\":\"北歐風（柔和淺灰色調）\"}。"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                        }
                    ]
                }
            ],
            max_tokens=300,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise RuntimeError(f"分類失敗：{e}\nerror: {response.choices[0].message.content}")


def classify_furniture_from_text(description: str, color_mode: str = "original") -> dict:
    """
    傳入一段家具描述，呼叫 GPT-4o 將其 parse 成：
        {"type":"sofa","style":"modern"}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                        f"以下是一段家具描述：\n\n"
                        f"{description}\n\n"
                        f"請以「{color_mode}」色彩模式想像此家具的配色，"
                        "然後**只**回傳一個 JSON 物件，包含兩個 key：\n"
                        "- \"type\": 家具的種類 (e.g. \"sofa\", \"chair\", ...)\n"
                        "- \"style\": 家具的風格與主要色調 (請在 style 裡同時描述風格與色調，例如 “modern（柔和淺灰色調）”)\n\n"
                        "**不要**額外的文字或說明，也不要回傳markdown格式，僅回應例如：\n"
                        "{\"type\":\"sofa\",\"style\":\"modern（柔和淺灰色調）\"}"
                        )
                    }
                ]
            }
            ],
            max_tokens=100,
        )
        
        # 直接把模型回傳的 JSON parse 回 dict
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        raise RuntimeError(f"分類失敗：{e}\nerror: {response.choices[0].message.content}")
