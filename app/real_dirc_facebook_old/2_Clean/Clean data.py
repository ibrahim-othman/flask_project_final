import pandas as pd
import ast  # For safely parsing strings into Python objects (like dicts)
from pathlib import Path
import json
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/" #modified, altough there must be smarter way to do this Ibrahim

# Load the CSV file


with open(root+"file_name_and_id.json", encoding="utf-8") as id_file:
    file_id = json.load(id_file)
file_name= file_id.get("file_id")
df = pd.read_csv(root + file_name + ".csv", encoding="utf-8-sig")

# --------- 1. Flatten nested columns ---------
# These columns contain dictionaries as strings and need to be converted
nested_columns = ['author', 'reactions']
for col in nested_columns:
    if col in df.columns:
        # Convert string representation of dictionaries to actual dicts
        df[col] = df[col].dropna().apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        normalized = pd.json_normalize(df[col])
        # Rename the new columns to avoid name conflicts
        normalized.columns = [f"{col}_{subcol}" for subcol in normalized.columns]
        df = pd.concat([df, normalized], axis=1)

# --------- 2. Convert timestamp to readable datetime (Cairo timezone) ---------
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo')
df['timestamp'] = df['timestamp'].dt.strftime('%d/%m/%Y')
# --------- 3. Drop unnecessary columns ---------
columns_to_drop = [
    'image', 'video', 'album_preview', 'video_files', 'video_thumbnail',
    'external_url', 'attached_event', 'attached_post', 'attached_post_url',
    'text_format_metadata','author','reactions'
]
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

# Save the cleaned data to a new CSV
df.to_csv(root+"cleaned_" + file_name + ".csv", encoding="utf-8-sig", index=False)

print("Data cleaned and saved to cleaned_results.csv")
