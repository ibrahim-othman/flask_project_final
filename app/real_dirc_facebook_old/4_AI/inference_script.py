import joblib
import pandas as pd
from pathlib import Path
import json
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/"

with open(root+"file_name_and_id.json", encoding="utf-8") as id_file:
    file_id = json.load(id_file)
file_name= file_id.get("file_id")

df = pd.read_json(root + "prepared_" + file_name + ".json", encoding="utf-8-sig", convert_dates=False)

# تحميل الموديل والـ vectorizer
base_dir = Path(__file__).resolve().parent
root2=str(base_dir)+ "/"
model = joblib.load(root2 + "best_sentiment_model.pkl")
vectorizer = joblib.load(root2 + "tfidf_vectorizer.pkl")

# تحويل عمود 'message' إلى تمثيل عددي باستخدام TF-IDF
X_messages = vectorizer.transform(df['message'])

# التنبؤ بالمشاعر
predictions = model.predict(X_messages)

# إضافة النتائج إلى الـ DataFrame
df['predicted_sentiment'] = predictions


# حفظ النتائج في ملف جديد
output_path = root + "final_" + file_name + ".json"
df.to_json(output_path, orient='records', force_ascii=False, indent=2)

print(f"✅ تم حفظ النتائج في الملف: {output_path}")
