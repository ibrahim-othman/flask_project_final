import subprocess
from pathlib import Path
from datetime import datetime
import json
import re
import pandas as pd
def run_all_scripts(query, start_date, end_date,request_id ,rquired_tweets = '100'):
    base_dir = Path(__file__).resolve().parent
    root=str(base_dir)+ "/"




    # Load existing JSON file
    with open(root+'1_Extract_data_from_twitter/'+"Constrains.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Assume only one dictionary in the list
    constraints = data[0]

    # Show current values
    print("Current values:")
    print(f"query: {constraints.get('query', '')}")
    print(f"start_date: {constraints.get('start_date', '')}")
    print(f"end_date (will be updated automatically): {constraints.get('end_date', '')}")

    print("\nEnter new values (press Enter to keep current value):")

    # Input for 'query'
    new_query = query.strip()
    if new_query:
        constraints['query'] = new_query

    # Input for 'start_date'
    new_start_date = start_date.strip()
    if new_start_date:
        constraints['start_date'] = new_start_date

    # Set end_date to today's date (format: YYYY-MM-DD)
    new_end_date = end_date.strip()
    if new_start_date:
        constraints['end_date'] = new_end_date

    # Save the updated JSON
    with open(root+'1_Extract_data_from_twitter/'+"Constrains.json", "w", encoding="utf-8") as file:
        json.dump([constraints], file, ensure_ascii=False, indent=4)

    print("\n✅ Constrain File updated successfully!")
    #------------------------------------------------------------------
    with open(root+"Choose_Number_of_tweets_and_output_name.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # We assume there's only one object in the list
    settings = data[0]

    print("Current values:")
    print(f"numberOfTweets: {settings.get('numberOfTweets', '')}")

    settings['request_id']=request_id
    # Prompt for file name
    new_file_name = str(request_id)
    if new_file_name:
        settings['fileName'] = new_file_name+'.json'

    # Prompt for number of tweets
    new_number = rquired_tweets.strip()
    if new_number.isdigit():
        settings['numberOfTweets'] = int(new_number)
        
        
    # Save back to the same file
    with open(root+"Choose_Number_of_tweets_and_output_name.json", "w", encoding="utf-8") as file:
        json.dump([settings], file, ensure_ascii=False, indent=4)

    print("\n✅ File updated successfully!")


    #-------------------------------------------------------------------

    subprocess.run(["python", root + "1_Extract_data_from_twitter/Extract_Data.py"], check=True)
    print("Data extraction completed successfully.")
    subprocess.run(["python", root + "2_clean files/Clean_Json.py"], check=True)
    print("Data cleaning completed successfully.")
    subprocess.run(["python", root + "3_perepare_data/prepare.py"], check=True)
    print("Data preparation completed successfully.")
    subprocess.run(["python", root + "4_AI/AI.py"], check=True)
    print("AI processing completed successfully.")
    
    with open(root+'final_'+settings['fileName'], "r", encoding="utf-8") as file:
        data = json.load(file)

    

        
    return (data,request_id)


if __name__ == "__main__":
    print("🔧 Please provide the following settings:\n")

    query = input("🔍 Query : ").strip()
    start_date = input("📅 Start Date (YYYY-MM-DD): ").strip()
    end_date = input("📅 End Date (YYYY-MM-DD): ").strip()
    required_tweets = input("🐦 Number of Tweets: ").strip()
    request_id = input("🆔 Request ID: ").strip()

    # Call the main function
    data,request_id= run_all_scripts(query, start_date,end_date, request_id,required_tweets)
    print(request_id)
