import sys, json, base64
import openai
from django.conf import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

# def classify_furniture_from_image(image_path, color_mode: str = "original"):
#     """
#     傳入一張本機圖片檔路徑，呼叫 GPT-4o 幫你回傳：
#       {"種類":"沙發","風格":"北歐風"}
#     """
#     try:
#         with open(image_path, "rb") as f:
#             b64 = base64.b64encode(f.read()).decode("utf-8")

#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": (
#                                 f"告訴我裡面的家具種類和風格（請在 style 裡同時描述風格與主要色調）是什麼？"
#                                 "請以「{color_mode}」的色彩方式轉換你看到的家具色調"
#                                 "(如果為互補色的轉換方式：紅色<->綠色、藍色<->橙色、黃色<->紫色、黑色<->白色...以此類推)"
#                                 "(如果為單色的轉換方式：選擇圖片中最主要的色調)"
#                                 "(如果為類似色的轉換方式：選擇圖片中最主要的色調，並將其轉換為類似的色調)"
#                                 "不要多任何額外文字。也不要回傳markdown格式。"
#                                 "然後**只**回傳一個 JSON 物件，包含兩個 key：\n"
#                                 "請**只回傳 JSON**格式，像這樣："
#                                 "{\"type\":\"沙發\",\"style\":\"北歐風（柔和淺灰色調）\"}。"
#                             )
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
#                         }
#                     ]
#                 }
#             ],
#             max_tokens=300,
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception as e:
#         raise RuntimeError(f"分類失敗：{e}\nerror: {response.choices[0].message.content}")
def classify_furniture_from_image(image_path, color_mode: str = "original"):
    """
    傳入一張本機圖片檔路徑，先請 GPT-4o 幫我們把圖片的家具種類、風格、主要色調轉換出來，
    再請 GPT-4o 幫我們把色調依照 color_mode 來轉換，並輸出最終的 JSON 物件。
    """
    try:
        # 讀取圖片並編碼成 base64
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        # STEP 1: 先請 GPT-4o 回傳家具種類、風格，以及主要色調（原始色調）
        response1 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "請告訴我圖片裡的家具種類、風格，並描述主要色調。\n"
                                "只回傳一個 JSON 物件，格式如下：\n"
                                "{\"type\":\"沙發\",\"style\":\"北歐風（主要色調：橙色）\"}\n"
                                "不要任何額外文字，也不要回傳 Markdown 格式。"
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
        raw_content = response1.choices[0].message.content
        raw_result = json.loads(raw_content)

        # 如果 color_mode 是 "original"，直接回傳第一階段的結果
        if color_mode == "original":
            return raw_result

        # STEP 2: 再請 GPT-4o 將原始色調依照 color_mode 處理，並回傳最終 JSON
        # 這邊將第一階段得到的 JSON 拿去做轉換，並請 GPT-4o 只更新 style 裡的色調描述
        response2 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "以下是一個 JSON 物件，請將其中 「style」 欄位的色調"
                                f"依照「{color_mode}」的方式做轉換（互補色、單色或類似色），"
                                "並回傳同樣格式的 JSON，只包含 type 與 style。不要額外文字，也不要 Markdown。\n\n"
                                f"{json.dumps(raw_result, ensure_ascii=False)}"
                            )
                        }
                    ]
                }
            ],
            max_tokens=300,
        )
        final_content = response2.choices[0].message.content
        return json.loads(final_content)

    except Exception as e:
        # 如果失敗，將錯誤訊息與 GPT 回應一併拋出
        raise RuntimeError(f"分類或色調轉換失敗：{e}\n原始回應（如果有）: {locals().get('raw_content', '')}")



# def classify_furniture_from_text(description: str, color_mode: str = "original") -> dict:
#     """
#     傳入一段家具描述，呼叫 GPT-4o 將其 parse 成：
#         {"type":"sofa","style":"modern"}
#     """
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": (
#                         f"以下是一段家具描述：\n\n"
#                         f"{description}\n\n"
#                         f"請以「{color_mode}」色彩模式想像此家具的配色，"
#                         "然後**只**回傳一個 JSON 物件，包含兩個 key：\n"
#                         "- \"type\": 家具的種類 (e.g. \"sofa\", \"chair\", ...)\n"
#                         "- \"style\": 家具的風格與主要色調 (請在 style 裡同時描述風格與色調，例如 “modern（柔和淺灰色調）”)\n\n"
#                         "**不要**額外的文字或說明，也不要回傳markdown格式，僅回應例如：\n"
#                         "{\"type\":\"sofa\",\"style\":\"modern（柔和淺灰色調）\"}"
#                         )
#                     }
#                 ]
#             }
#             ],
#             max_tokens=100,
#         )
        
#         # 直接把模型回傳的 JSON parse 回 dict
#         return json.loads(response.choices[0].message.content)

#     except Exception as e:
#         raise RuntimeError(f"分類失敗：{e}\nerror: {response.choices[0].message.content}")
def classify_furniture_from_text(description: str, color_mode: str = "original") -> dict:
    """
    傳入一段家具描述，先請 GPT-4o 幫我們把文字的家具種類、風格與主要色調 parse 出來，
    再請 GPT-4o 幫我們將色調依照 color_mode 來轉換，並輸出最終的 JSON 物件。
    """
    try:
        # STEP 1: 先請 GPT-4o 回傳家具種類、風格，以及主要色調（原始色調）
        response1 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "以下是一段家具描述，請幫我解析成家具的「種類」、「風格」"
                                "，並同時描述「主要色調」。\n\n"
                                f"{description}\n\n"
                                "只回傳一個 JSON 物件，格式如下：\n"
                                "{\"type\":\"sofa\",\"style\":\"modern（主要色調：橙色）\"}\n"
                                "不要任何額外文字或說明，也不要回傳 Markdown 格式。"
                            )
                        }
                    ]
                }
            ],
            max_tokens=100,
        )
        raw_content = response1.choices[0].message.content
        raw_result = json.loads(raw_content)

        # 如果 color_mode 是 "original"，直接回傳第一階段的結果
        if color_mode == "original":
            return raw_result

        # STEP 2: 再請 GPT-4o 將原始色調依照 color_mode 處理，並回傳最終 JSON
        # 這裡將第一階段得到的 JSON 拿去做轉換，只更新 style 中的色調描述
        response2 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "以下是一個 JSON 物件，請將其中 “style” 欄位裡的「主要色調」"
                                f"依照「{color_mode}」的方式做轉換（互補色、單色或類似色），"
                                "並回傳相同格式的 JSON，只包含 type 與 style。"
                                "不要任何額外文字或說明，也不要 Markdown。\n\n"
                                f"{json.dumps(raw_result, ensure_ascii=False)}"
                            )
                        }
                    ]
                }
            ],
            max_tokens=100,
        )
        final_content = response2.choices[0].message.content
        return json.loads(final_content)

    except Exception as e:
        # 如果失敗，將錯誤訊息與 GPT 回應一併拋出（若有 raw_content）
        raise RuntimeError(f"分類或色調轉換失敗：{e}\n原始回應（如果有）：{locals().get('raw_content', '')}")

