from camel_tools.sentiment import SentimentAnalyzer
import json

#with open('prepared_clean_labn1.json', 'r', encoding='utf-8') as f:
#    data = json.load(f)

# Accessing the first tweet's text
#print(data[0]['text'])

sa = SentimentAnalyzer.pretrained()



# Predict the sentiment of multiple sentences
sentences = [
    'أنا بخير',
    'أنا لست بخير',
    'انا لا العب الكره'
]
sentiments = sa.predict(sentences)
print(sentiments)
