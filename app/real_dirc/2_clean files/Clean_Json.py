import pandas as pd
import json

import os ,string
#path
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
root=str(base_dir)+ "/"


df=pd.read_json(root+"Choose_Number_of_tweets_and_output_name.json")
file_name =root+ df['fileName'][0]  # Assuming the file name is in the first row of the DataFrame
saved_file_name =root+'cleaned_'+df['fileName'][0]
with open(file_name, 'r', encoding='utf-8') as file:
    file_data = file.read()

json_objects = file_data.splitlines()

modified_json_objects = []

for json_object in json_objects:
    try:
        json_data = json.loads(json_object)

        keys_to_remove = [
            "media_url", "video_url", "is_private", "profile_pic_url", "profile_banner_url",
            "description", "external_url", "timestamp", "has_nft_avatar", "category", "default_profile",
            "default_profile_image", "listed_count", "retweet", "in_reply_to_status_id",
            "quoted_status_id", "binding_values", "expanded_url", "retweet_tweet_id", "extended_entities",
            "conversation_id", "retweet_status", "quoted_status", "bookmark_count", "community_note"
        ]

        for key in keys_to_remove:
            if key in json_data:
                del json_data[key]

        if "extended_entities" in json_data:
            extended_entities = json_data["extended_entities"]
            if "media" in extended_entities:
                for media_item in extended_entities["media"]:
                    if "display_url" in media_item:
                        del media_item["display_url"]
                    if "ext_media_availability" in media_item and "status" in media_item["ext_media_availability"]:
                        del media_item["ext_media_availability"]["status"]

        user_keys_to_remove = [
            "is_private", "profile_pic_url", "profile_banner_url", "external_url",
            "timestamp", "has_nft_avatar", "category", "listed_count", "verified_type", "default_profile",
            "default_profile_image"
        ]

        if "user" in json_data:
            for key in user_keys_to_remove:
                if key in json_data["user"]:
                    del json_data["user"][key]

        modified_json_objects.append(json_data)

    except json.JSONDecodeError:
        print("Error in reading json object!")
        continue

# Save as a list of JSON objects

with open(saved_file_name, 'w', encoding='utf-8') as file:
    json.dump(modified_json_objects, file, indent=4, ensure_ascii=False)

print("Data has been cleaned and saved as a list of JSON objects!")
