import joblib

# تحميل الموديل والفيكتورايزر
model = joblib.load("best_sentiment_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# مثال لتجربة النص
sample_text = "هذه تجربة رائعة جدًا"
X_sample = vectorizer.transform([sample_text])
prediction = model.predict(X_sample)

print(f"✅ Exception: {prediction[0]}")
