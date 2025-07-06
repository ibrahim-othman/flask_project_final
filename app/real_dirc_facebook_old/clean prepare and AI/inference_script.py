import joblib
import pandas as pd
from pathlib import Path
base_dir = Path(__file__).resolve().parent
root=str(base_dir)+ "/"


df = pd.read_json(root + "normalized_cleaned_results.json", encoding="utf-8-sig")

# تحميل الموديل والـ vectorizer
model = joblib.load(root + "best_sentiment_model.pkl")
vectorizer = joblib.load(root + "tfidf_vectorizer.pkl")

# تحويل عمود 'message' إلى تمثيل عددي باستخدام TF-IDF
X_messages = vectorizer.transform(df['message'])

# التنبؤ بالمشاعر
predictions = model.predict(X_messages)

# إضافة النتائج إلى الـ DataFrame
df['predicted_sentiment'] = predictions


# حفظ النتائج في ملف جديد
output_path = root + "predicted_sentiments.json"
df.to_json(output_path, orient='records', force_ascii=False, indent=2)

print(f"✅ تم حفظ النتائج في الملف: {output_path}")
