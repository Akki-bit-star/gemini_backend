import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_response(self, message: str) -> str:
        try:
            response = self.model.generate_content(message)
            print("Response in gemini service:", response.text)
            return response.text
        except Exception as e:
            return f"Sorry, I couldn't process your request. Error: {str(e)}"
