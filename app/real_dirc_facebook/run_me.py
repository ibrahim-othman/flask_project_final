import subprocess
import json
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(__file__))

from Translate import smart_translate  # تأكد أن الملف اسمه translate.py ويحتوي على الدالة
base_dir = Path(__file__).resolve().parent
root = str(base_dir) + "/"

def run_facebook(query_input, start_date, end_date,request_id ,required_tweets = '100'):
    # تحميل ملف الإعدادات الحالي
    with open(root + "config.json", "r", encoding="utf-8") as file:
        constraints = json.load(file)
    if query_input:
        query_list = [q.strip() for q in query_input.split(",") if q.strip()]
        translated_queries = []
        for query in query_list:
            translated = smart_translate(query)
            print(f"🔁 ترجمة '{query}' ➜ '{translated}'")
            translated_queries.append(translated)
        constraints['queries'] = translated_queries

    if start_date:
        constraints['start_date'] = start_date

    if end_date:
        constraints['end_date'] = end_date

    if required_tweets:
        constraints['posts'] = required_tweets
        constraints['posts_target'] = int(required_tweets)

    # حفظ التعديلات في ملف config.json
    with open(root + "config.json", "w", encoding="utf-8") as file:
        json.dump(constraints, file, ensure_ascii=False, indent=4)

    # تعديل ملف file_name_and_id.json
    with open(root + "file_name_and_id.json", "r", encoding="utf-8") as file:
        id_file = json.load(file)

    if request_id:
        id_file['file_id'] = str(request_id)

    with open(root + "file_name_and_id.json", "w", encoding="utf-8") as file:
        json.dump(id_file, file, ensure_ascii=False, indent=4)

    # تنفيذ السكربتات
    subprocess.run(["python", root + "project.py"], check=True)
    print("✅ Data extraction completed successfully.")

    subprocess.run(["python", root + "2_Clean/Clean data.py"], check=True)
    print("✅ Data cleaning completed successfully.")

    subprocess.run(["python", root + "3_prepare/prep_data_f.py"], check=True)
    print("✅ Data preparation completed successfully.")

    subprocess.run(["python", root + "4_AI/inference_script.py"], check=True)
    print("✅ AI processing completed successfully.")

    # قراءة النتائج النهائية
    with open(root + "final_" + id_file['file_id'] + ".json", "r", encoding="utf-8") as file:
        final_data = json.load(file)

    return (final_data, id_file['file_id'])

def edit(root=root):
    # إدخال البيانات من المستخدم
    query_input = input("Query (separate multiple queries with commas): ").strip()
    start_date = input("Start Date (YYYY-MM-DD): ").strip()
    end_date = input("End Date (YYYY-MM-DD): ").strip()
    required_tweets = input("Number of posts: ").strip()
    request_id = input("Request ID: ").strip()


    print("\nEnter new values (press Enter to keep current value):")


if __name__ == "__main__":
    (data, file_id) = edit(root)
    print(data)
