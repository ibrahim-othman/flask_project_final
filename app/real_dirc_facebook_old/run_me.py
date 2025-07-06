import subprocess
import json
from pathlib import Path
base_dir = Path(__file__).resolve().parent
root=str(base_dir)+ "/"

def run_facebook(query, start_date, end_date,request_id ,required_tweets = '100'):

    with open(root + "config.json", "r", encoding="utf-8") as file:
        constraints = json.load(file)

    # Assume values like query, start_date, etc. already exist

    new_query = query#.strip()
    if new_query:
        constraints['queries'] = new_query

    new_start_date = start_date.strip()
    if new_start_date:
        constraints['start_date'] = new_start_date

    new_end_date = end_date.strip()
    if new_end_date:
        constraints['end_date'] = new_end_date

    posts = required_tweets.strip()
    if posts:
        constraints['posts'] = posts
        
    posts_target = required_tweets.strip()
    if posts:
        constraints['posts_target'] = int(posts_target)
    # Save back to file
    with open(root + "config.json", "w", encoding="utf-8") as file:
        json.dump(constraints, file, ensure_ascii=False, indent=4)

#-------------------------------------------------------------------------

    with open(root + "file_name_and_id.json", "r", encoding="utf-8") as file:
        id_file = json.load(file)

    # Assume values like query, start_date, etc. already exist
    print("\nEnter new values (press Enter to keep current value):")

    file_id = str(request_id)#.strip()
    if file_id:
        id_file['file_id'] = file_id

    with open(root + "file_name_and_id.json", "w", encoding="utf-8") as file:
        json.dump(id_file, file, ensure_ascii=False, indent=4)

#-------------------------------------------------------------------------
    # Run the scripts in sequence
    
    subprocess.run(["python", root + "project.py"], check=True)
    print("Data extraction completed successfully.")
    subprocess.run(["python", root + "2_Clean/Clean data.py"], check=True)
    print("Data cleaning completed successfully.")
    subprocess.run(["python", root + "3_prepare/prep_data_f.py"], check=True)
    print("Data preparation completed successfully.")
    subprocess.run(["python", root + "4_AI/inference_script.py"], check=True)
    print("AI processing completed successfully.")
    
    with open(root + "final_"+str(id_file['file_id'])+".json", "r", encoding="utf-8") as file:
        final_data = json.load(file)
    return (final_data,id_file['file_id'])
def edit(root=root):
    query = input("Query : ").strip()
    start_date = input(" Start Date (YYYY-MM-DD): ").strip()
    end_date = input("End Date (YYYY-MM-DD): ").strip()
    required_tweets = input(" Number of posts: ").strip()
    request_id = input(" Request ID: ").strip()
    run_facebook(query, start_date,end_date, request_id,required_tweets)
    print("\nEnter new values (press Enter to keep current value):")

if __name__ == "__main__":
    (data,id)=edit(root)
    print(data)
