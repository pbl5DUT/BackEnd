import os
import google.generativeai as genai
from rest_framework.decorators import api_view
from rest_framework.response import Response

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@api_view(["POST"])
def chat_with_gpt(request):
    messages = request.data.get("messages", [])

    if not isinstance(messages, list):
        return Response({"error": "messages phải là một list"}, status=400)

    # Gộp prompt từ tất cả message, có role user hoặc assistant để giữ bối cảnh (tuỳ bạn)
    prompt = "\n".join([m.get("content", "") for m in messages if m.get("role") == "user"])

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        return Response({"reply": response.text})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
