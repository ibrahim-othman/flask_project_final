import modify_the_api_tweets_file 
import Choice_Apis
import json
from datetime import date,datetime,timedelta
import requests
import pandas as pd
import os ,string
#path
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
print(base_dir)
root=str(base_dir)+ "/"

df=pd.read_json(root+"Choose_Number_of_tweets_and_output_name.json")
file_name=df['fileName'][0]

apis_list=Choice_Apis.APIs_Will_Be_Used
output_file_name=root+file_name

def append_data_into_json(file_name, json_data_list):
    with open(file_name, "a", encoding="utf-8") as file:  
        for data in json_data_list:
            json.dump(data, file, ensure_ascii=False)  
            file.write('\n')


def choice_api_index(apis_list=apis_list):
    index=0
    for api in apis_list :
        total_requests_we_take_per_API=api['total_requests_we_take_per_API']
        if total_requests_we_take_per_API>0:
            return index
        index+=1
    return -1


def extract_if_interval_time_more_than_one(apis_list=apis_list,interval_date=Choice_Apis.intervals_days_from_request_to_other,Constrains=Choice_Apis.Constrains , output_file_name=output_file_name):
    querystring ={}
    for q in Constrains :
        querystring[q]=Constrains.iloc[0][q]
    
    count=0
    for api in apis_list:
        total_requests_we_take_per_API=int(api['total_requests_we_take_per_API'])

        for request in range(total_requests_we_take_per_API):
            
            url=api['url']
            headers = {"x-rapidapi-key":api["x-rapidapi-key"],
	                   "x-rapidapi-host" :api["x-rapidapi-host"]
                        }
            
            end_date= datetime.strptime(querystring["start_date"], "%Y-%m-%d")+timedelta(days=interval_date)
            querystring["end_date"] = end_date.strftime('%Y-%m-%d')# Convert back to string
            

                # Update sdate for the next iteration
            
            response = requests.get(url, headers=headers, params=querystring)
            results = response.json().get('results', [])
            print(count,querystring["start_date"],querystring["end_date"] )
            count+=1
            append_data_into_json(output_file_name,results)
            querystring["start_date"]=querystring["end_date"]
            
 
 
 
 

def make_many_requests_per_day(apis_list,number_of_req_per_day,querystring,output_file_name=output_file_name):
    
    
    for request in range(int(number_of_req_per_day)):
            
            print(querystring["start_date"],querystring["end_date"],int(number_of_req_per_day))
            api_index=choice_api_index()
            if(api_index==-1):
                break
            
            url=apis_list[api_index]['url']
            headers = {"x-rapidapi-key":apis_list[api_index]["x-rapidapi-key"],
	                   "x-rapidapi-host" :apis_list[api_index]["x-rapidapi-host"]
                        }
            
            response = requests.get(url, headers=headers, params=querystring)
            results = response.json().get('results', [])
            
            append_data_into_json(output_file_name,results)
            
            continuation_token = response.json().get('continuation_token', None)
            querystring['continuation_token'] = continuation_token
            apis_list[api_index]['total_requests_we_take_per_API']=apis_list[api_index]['total_requests_we_take_per_API']-1
            
            
 
def extract_if_interval_time_less_than_or_equal_one(apis_list=apis_list,number_of_req_per_day=Choice_Apis.Number_of_requests_per_day \
                                                     ,reminder_request=Choice_Apis.Number_of_reminder_requests,\
                                                         Constrains=Choice_Apis.Constrains, days=Choice_Apis.number_of_days):
    querystring ={}
    for q in Constrains :
        querystring[q]=Constrains.iloc[0][q]
    for day in range(days):

        
        end_date= datetime.strptime(querystring["start_date"], "%Y-%m-%d")+timedelta(days=1)
        querystring["end_date"] = end_date.strftime('%Y-%m-%d')# Convert back to string
        
        make_many_requests_per_day(apis_list,number_of_req_per_day,querystring)
        
        if reminder_request :
             make_many_requests_per_day(apis_list,1,querystring)
             reminder_request-=1
             
        querystring["start_date"] = querystring["end_date"]
        
        

if(Choice_Apis.intervals_days_from_request_to_other >1 ):
    extract_if_interval_time_more_than_one()
else : 
    extract_if_interval_time_less_than_or_equal_one()
