import pandas as pd 
import prepare_arabic_data 



import os ,string
#path
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/"

df=pd.read_json(root+"Choose_Number_of_tweets_and_output_name.json") 
file_path =root+ 'cleaned_'+df['fileName'][0] 
output_name = root + 'prepared_'+df['fileName'][0]


origina_text = pd.read_json(file_path, encoding='utf-8', dtype={"tweet_id": str}) 

origina_text_column=origina_text['text']

normalized_text=[] 
for text in origina_text_column : 
    normalized_text.append(prepare_arabic_data.simple_normalize(text)) 

origina_text['text']=normalized_text
origina_text.to_json(output_name, orient='records', force_ascii=False, indent=4) 