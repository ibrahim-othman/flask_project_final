import json  
import pandas as pd
import re

import os ,string
#path
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/"

df=pd.read_json(root+"Choose_Number_of_tweets_and_output_name.json")
file_path = root + 'prepared_'+df['fileName'][0]
output_name = root + 'final_'+df['fileName'][0]
with open(file_path, 'r', encoding='utf-8') as f: 
    data = json.load(f)



import sys
sys.path.append(root+'4_AI/camel_tools-master')
from camel_tools.sentiment import SentimentAnalyzer
sa = SentimentAnalyzer.pretrained()


new_data = []
for tweet in data:
    text = tweet.get("text", "").strip()
    if text:
        sentiment = sa.predict_sentence(text)
    else:
        sentiment = "unknown"
    
    tweet_with_sentiment = tweet.copy()
    tweet_with_sentiment["sentiment"] = sentiment
    new_data.append(tweet_with_sentiment)



with open(root+df['fileName'][0], "r", encoding="utf-8") as file:
    raw_data = file.read().splitlines()
texts = [json.loads(line)['text'] for line in raw_data if line]
final_text = []
for text in texts:
     # Normalize the text
    text = text.lower()
    text = re.sub(r"http\S+|www.\S+", '', text)  # إزالة الروابط
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)  # إزالة الإيميلات
    text = ' '.join(text.split())  # إزالة المسافات الزائدة
    final_text.append(text)

for i in range(len(new_data)):
    new_data[i]["text"] = final_text[i]
    
with open(output_name, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

