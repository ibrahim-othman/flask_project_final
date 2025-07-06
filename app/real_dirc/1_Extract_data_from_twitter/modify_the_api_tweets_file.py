import Choice_Apis
import json
import csv
import datetime
import os

import os ,string
#path
from pathlib import Path

base_dir = Path(__file__).resolve().parent


apis_list = Choice_Apis.APIs_Will_Be_Used
root =str(base_dir.parent) + "/Airflow_file_to_track_the_Api_history/files"+"/"

def write_api_used_in_csv_history(apis_list=apis_list):
    fieldnames = ['url','x-rapidapi-key', 'x-rapidapi-host',  'date','used']  # Adjust fieldnames based on your API data structure

    with open(root+"API_History.csv", 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header if the file is new
        if file.tell() == 0:
            writer.writeheader()
        
        for api in apis_list:
            api_data = {
                'url': api.get('url', ''),
                'x-rapidapi-key': api.get('x-rapidapi-key', ''),
                'x-rapidapi-host': api.get('x-rapidapi-host', ''),
                'date': datetime.date.today().strftime('%Y-%m-%d'),
                'used':api.get('total_requests_we_take_per_API',0)
            }
            writer.writerow(api_data)  # Use writerow instead of csv.dump
    print("Api History is modified")
    
    


def modify_apis(apis_list=apis_list,file_path=root+'API_file.json'):
    with open(file_path, 'r') as file:
        apis = json.load(file)
    
    final_api=[]
    # Update Avilabe_requests_per_month for matching APIs
    for main_api in apis:
        
        for used_api in apis_list :
            
            if main_api['url'] == used_api['url'] \
                and main_api['x-rapidapi-key'] == used_api['x-rapidapi-key'] \
                    and main_api['x-rapidapi-host'] == used_api['x-rapidapi-host'] :
                main_api['Avilabe_requests_per_month'] -=int(used_api['total_requests_we_take_per_API'])
                if(main_api['Avilabe_requests_per_month']<0):
                    main_api['Avilabe_requests_per_month']=0
                    
        final_api.append(main_api)
    # Write updated data back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(final_api, file, indent=4)
        print("Api file is modified")
    
    
write_api_used_in_csv_history()

modify_apis()
