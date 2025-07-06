from camel_tools.sentiment import SentimentAnalyzer

sa = SentimentAnalyzer.pretrained()

# Predict the sentiment of a single sentence
sentiment = sa.predict_sentence('أنا بخير')

# Predict the sentiment of multiple sentences
sentences = [
    'أنا بخير',
    'أنا لست بخير',
    'انا لا العب الكره'
]
sentiments = sa.predict(sentences)
print(sentiments)