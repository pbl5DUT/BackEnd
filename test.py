import google.generativeai as genai

genai.configure(api_key="AIzaSyAn_FRZPo7wTpP6eG2Jh6w3qKcOiC0Qv8Q")

models = genai.list_models()
for m in models:
    print(m.name, m.supported_generation_methods)
