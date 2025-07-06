import http.client
import json
import pandas as pd
import time
import random
import os
import urllib.parse
from datetime import datetime
from pathlib import Path

base_dir = Path(__file__).resolve().parent
root = str(base_dir) + "/"

# قراءة الإعدادات
with open(root + "config.json", encoding="utf-8") as config_file:
    config = json.load(config_file)

with open(root + "file_name_and_id.json", encoding="utf-8") as file_id_file:
    file_id = json.load(file_id_file)

QUERIES = config.get("queries", [config.get("query", "")])
START_DATE = config.get("start_date")
END_DATE = config.get("end_date")
POSTS_TARGET = int(config["posts_target"])
API_KEYS = config["RAPIDAPI_KEYS"]
API_HOST = config["RAPIDAPI_HOST"]

CSV_FILE = root + file_id.get("file_id") + ".csv"
LOG_FILE = root + "keys_usage.log"
key_usage = [0] * len(API_KEYS)
posts_collected_per_key = [0] * len(API_KEYS)
remaining_per_key = ["?"] * len(API_KEYS)

# تحميل البيانات السابقة إن وجدت
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    seen_posts = set(df["Post ID"].astype(str)) if "Post ID" in df.columns else set()
    data = df.to_dict(orient="records")
else:
    seen_posts = set()
    data = []

def log_usage(index, status):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(
            f"[{datetime.now()}] Key {index + 1} ({API_KEYS[index][:10]}...): "
            f"{status} | Remaining: {remaining_per_key[index]} | Posts collected: {posts_collected_per_key[index]}\n"
        )

post_count = 0  # إجمالي عدد البوستات المجمعة لكل الاستعلامات
num_queries = len(QUERIES)
posts_per_query = POSTS_TARGET // num_queries  # توزيع متساوي لكل كويري
remainder_posts = POSTS_TARGET % num_queries  # باقي القسمة لتوزيعه بعدين

for idx, query in enumerate(QUERIES):
    current_cursor = None
    key_index = 0
    headers_printed = False

    # لو فيه باقي من القسمة نضيفه لأول استعلامات
    target_for_this_query = posts_per_query + (1 if idx < remainder_posts else 0)
    query_post_count = 0  # عدد البوستات المجمعة لهذا الكويري فقط

    while query_post_count < target_for_this_query and key_index < len(API_KEYS):
        try:
            api_key = API_KEYS[key_index]
            conn = http.client.HTTPSConnection(API_HOST)
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": API_HOST
            }

            encoded_query = urllib.parse.quote(query)
            request_url = f"/search/posts?query={encoded_query}"
            if START_DATE:
                request_url += f"&start_date={START_DATE}"
            if END_DATE:
                request_url += f"&end_date={END_DATE}"
            if current_cursor:
                request_url += f"&cursor={current_cursor}"

            conn.request("GET", request_url, headers=headers)
            res = conn.getresponse()

            if not headers_printed:
                # print("=== Response Headers ===")
                # for h in res.getheaders():
                #     print(f"{h[0]}: {h[1]}")
                headers_printed = True

            remaining = res.getheader("x-ratelimit-requests-remaining")
            if remaining and remaining.isdigit():
                remaining_per_key[key_index] = int(remaining)
            else:
                remaining_per_key[key_index] = "?"

            print(f"[INFO] Remaining requests: {remaining_per_key[key_index]}")

            if res.status == 429:
                print(f"[!] Key {key_index + 1} hit rate limit. Switching...")
                log_usage(key_index, "Rate limit (429)")
                key_index += 1
                continue

            if res.status != 200:
                print(f"[!] Request failed: Status {res.status}")
                log_usage(key_index, f"Request failed with status {res.status}")
                break

            response_data = res.read()
            json_data = json.loads(response_data)

            for result in json_data.get("results", []):
                post_id = str(result.get("post_id"))
                if post_id in seen_posts or query_post_count >= target_for_this_query:
                    continue
                seen_posts.add(post_id)

                result["Post ID"] = post_id
                data.append(result)
                post_count += 1
                query_post_count += 1
                posts_collected_per_key[key_index] += 1

            current_cursor = json_data.get("cursor")
            key_usage[key_index] += 1
            log_usage(key_index, f"Success")

            time.sleep(random.uniform(1.5, 3.0))

            if query_post_count >= target_for_this_query:
                print(f"[INFO] Reached target for query '{query}'. Moving to next query.")
                break

            if not current_cursor:
                print(f"No more data to fetch for query '{query}'.")
                break

        except KeyboardInterrupt:
            print("\n[!] Process interrupted by user. Saving data...")
            break
        except json.JSONDecodeError:
            print("[!] JSON decode error.")
            log_usage(key_index, "JSON decode error")
            break
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            log_usage(key_index, f"Exception: {e}")
            key_index += 1
            continue

    if post_count >= POSTS_TARGET:
        print("[INFO] Reached total posts target across all queries. Stopping data collection.")
        break

final_df = pd.DataFrame(data)
if "Post ID" not in final_df.columns:
    print("[!] 'Post ID' column not found in data. Skipping duplicate removal.")
else:
    final_df = final_df.drop_duplicates(subset="Post ID")

final_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

with open(LOG_FILE, "a", encoding="utf-8") as log_file:
    log_file.write(f"\n=== Summary of Key Usage ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")
    for i in range(len(API_KEYS)):
        log_file.write(
            f"Key {i + 1} ({API_KEYS[i][:10]}...): "
            f"{key_usage[i]}/{remaining_per_key[i]} requests used | "
            f"Posts collected: {posts_collected_per_key[i]}\n"
        )
    log_file.write("============================\n\n")

print("✅ Data saved and updated successfully to results_pandas.csv")
