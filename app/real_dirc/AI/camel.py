from camel_tools.sentiment import SentimentAnalyzer

# Specify the path to the sentiment analysis model
model_path = 'C:\\Users\\Esayed\\anaconda3\\Lib\site-packages\camel_tools\sentiment'  # Update if needed

# Initialize the sentiment analyzer
analyzer = SentimentAnalyzer()

# Sample Arabic text
text = "أنا حزين"

# Analyze sentiment
sentiment = analyzer.predict(text)

# Print the result
print(f"Sentiment: {sentiment}")