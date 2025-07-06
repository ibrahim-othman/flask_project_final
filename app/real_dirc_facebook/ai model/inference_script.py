import joblib
import joblib
import pandas as pd
from pathlib import Path
import json

# تحميل الموديل والـ vectorizer
base_dir = Path(__file__).resolve().parent
root2=str(base_dir)+ "/"

# تحميل الموديل والفيكتورايزر
model = joblib.load(root2 + "best_sentiment_model.pkl")
vectorizer = joblib.load(root2 + "tfidf_vectorizer.pkl")

# مثال لتجربة النص
sample_text = "هذه تجربة رائعة جدًا"
X_sample = vectorizer.transform([sample_text])
prediction = model.predict(X_sample)

print(f"✅ Exception: {prediction[0]}")
