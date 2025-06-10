from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
import re
import google.generativeai as genai

from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

# Kết nối CSDL
db = SQLDatabase.from_uri("mysql+mysqlconnector://root@localhost:3306/pbl5_1")

# Khởi tạo LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Khởi tạo SQL chain
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, return_intermediate_steps=True)


def clean_sql(raw_sql):
    raw_sql = raw_sql.strip()
    # Lấy nội dung giữa ```sql ... ```
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw_sql, re.DOTALL | re.IGNORECASE)
    if match:
        raw_sql = match.group(1).strip()
    # Xóa ký tự thừa
    raw_sql = raw_sql.strip("`").strip()
    return raw_sql

@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            if not question:
                return JsonResponse({"error": "Thiếu câu hỏi"}, status=400)

            # 1. Prompt gốc của LangChain (được dùng trong SQLDatabaseChain)
            _sql_prompt = PromptTemplate.from_template("""
            Based on the following table schema:

            {table_info}

            Translate the following question into a SQL query:
            Question: {input}
            SQL Query:
            """)

            # 2. Tạo LLMChain chỉ để sinh SQL thôi (không thực thi)
            sql_generator = LLMChain(
                llm=llm,
                prompt=_sql_prompt
            )

            # 3. Lấy thông tin bảng (để Gemini dùng khi sinh SQL)
            table_info = db.get_table_info()

            # 4. Gọi sinh SQL
            response = sql_generator.invoke({
                "input": question,
                "table_info": table_info
            })
            sql = response["text"].strip()
            print("⚠️ SQL sinh ra (chưa clean):", sql)
            sql = sql.replace("STRFTIME", "DATE_FORMAT")
            sql = re.sub(r"DATE_FORMAT\(\s*'(%[^']+)',\s*(\w+)\s*\)", r"DATE_FORMAT(\2, '\1')", sql)

            # 2. Làm sạch SQL nếu cần
            raw_sql = clean_sql(sql)
            print("🧹 SQL sau khi clean:", repr(raw_sql))
    

            # 3. Chỉ cho phép SELECT
            if not raw_sql.lower().startswith("select"):
                return JsonResponse({"error": "Chỉ cho phép câu lệnh SELECT."}, status=400)

            # 4. Kiểm tra bảng tồn tại
            table_names = db.get_table_names()
            tables_in_sql = re.findall(r"from\s+?(\w+)?", raw_sql, re.IGNORECASE)
            for t in tables_in_sql:
                if t not in table_names:
                    return JsonResponse({"error": f"Bảng '{t}' không tồn tại trong DB."}, status=400)

            # 5. Thực thi câu SQL
            print(raw_sql)
            try:
                query_result = db.run(raw_sql)
                print("✅ SQL thực thi thành công.")
            except Exception as e:
                print(f"❌ Lỗi khi thực thi SQL: {e}")
                return JsonResponse({"error": f"Lỗi khi thực thi SQL: {str(e)}"}, status=500)

            # 6. Xử lý kết quả trả về
            columns = query_result.keys() if hasattr(query_result, 'keys') else []
            data = [dict(zip(columns, row)) for row in query_result] if columns else query_result

            return JsonResponse({
                "raw_sql": raw_sql,
                "query_result": data,
            })

        except Exception as e:
            print(f"❌ Lỗi xử lý tổng: {e}")
            return JsonResponse({"error": f"Lỗi xử lý: {str(e)}"}, status=500)

    return JsonResponse({"error": "Phương thức không được hỗ trợ"}, status=405)