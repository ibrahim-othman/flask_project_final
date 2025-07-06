import sys
import json
import re
from googletrans import Translator
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

dictionary_path = Path(__file__).parent / "dictionary.json"
with open(dictionary_path, encoding='utf-8') as f:
    custom_dict = json.load(f)

def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def smart_translate(word):
    word = word.strip().lower()

    if is_arabic(word):
        return word  # بالفعل بالعربية، نرجعها زي ما هي

    if word in custom_dict:
        return custom_dict[word]

    translator = Translator()
    return translator.translate(word, src='en', dest='ar').text
