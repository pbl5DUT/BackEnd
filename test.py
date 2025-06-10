import google.generativeai as genai

genai.configure(api_key="AIzaSyA0ttf-9d1Cq0Esx_RMN4qyEOpBm0BB2q4")

models = genai.list_models()
for m in models:
    print(m.name, m.supported_generation_methods)
