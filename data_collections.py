import requests
import json
import time
import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from IPython.display import clear_output
import pandas as pd

bggdf = pd.read_csv('bgg_dataset.csv',sep=';')

## fill null ids from board game ids
nullId = [
    {'Ace of Aces: Jet Eagles':'1991'},
    {'Die Erben von Hoax':'413'},
    {'Rommel in North Africa: The War in the Desert 1941-42':'11113'},
    {'Migration: A Story of Generations':'143663'},
    {'Die Insel der steinernen Wachter':'54501'},
    {'Dragon Ball Z TCG (2014 edition)':'168077'},
    {'Dwarfest':'170337'},
    {'Hus':'25999'},
    {'Contrario 2':'27227'},
    {'Warage: Extended Edition':'198886'},
    {'Rainbow':'73574'},
    {'Sexy, el juego del arte del flirteo':'148211'},
    {"Dracarys Dice Don't Get Burned!":'269573'},
    {'Battleship: Tactical Capital Ship Combat 1925-1945':'8173'},
    {'The Umbrella Academy Game':'316555'},
    {'Hidden Conflict':'15804'}
]

id_map = {list(d.keys())[0]: list(d.values())[0] for d in nullId}

# Fill missing IDs
bggdf['ID'] = bggdf.apply(lambda row: id_map.get(row['Name'], row['ID']), axis=1)

gamesId = bggdf['ID'].tolist()
gamesId = [str(int(x)) for x in bggdf['ID']]







# Data collection

'''
### Get the market products using the geekdo API 
 - calculates the running time of each request and saves it to a txt
 - Calls API by changing page number and board game id
 - 2 second wait per page request and 1 second wait per board game
 - save error if it doesnt fetch the data
 - retrys to the next page if it fails to retrieve data from a specific page
 - saves data in the form of a csv, or and json, if it gets invalid json error

Important data include:
  - productid
  - objectid
  - price
  - currency
  - condition
  - version_name
  - game_name

#### IMPORTANT: The total running time to get all the data might take even days.
'''

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
SAVE_DIR = "geekdo_products_csv"
JSON_DIR = os.path.join(SAVE_DIR, "json")
ERROR_DIR = os.path.join(SAVE_DIR, "errors")
RUNTIME_FILE = os.path.join(SAVE_DIR, "runtime_log.txt")

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(ERROR_DIR, exist_ok=True)


base_url = (
    "https://api.geekdo.com/api/market/products?"
    "ajax=1&browsetype=browse&colluserid=0&condition=any&country=any&currency=any&"
    "displaymode=list&findmywants=0&inventorytype=any&marketdomain=boardgame&nosession=1&"
    "objectid={gameId}&objecttype=thing&pageid={page}&productstate=active&shiparea=any&"
    "sort=recent&stock=instock&userid=0"
)

# ---------------------------------------------------
# Load previous runtime
# ---------------------------------------------------
if os.path.exists(RUNTIME_FILE):
    try:
        with open(RUNTIME_FILE, "r", encoding="utf-8") as f:
            last_line = f.readlines()[-1]
            total_runtime = float(last_line.split("Total:")[-1].replace("s", "").strip())
    except:
        total_runtime = 0.0
else:
    total_runtime = 0.0
    

# ===================================================
# MAIN LOOP
# ===================================================
for gameId in tqdm(gamesId, desc="Fetching games", unit="game"):

    output_csv = os.path.join(SAVE_DIR, f"geekdo_product_{gameId}.csv")
    output_json = os.path.join(JSON_DIR, f"geekdo_product_{gameId}.json")
    error_file = os.path.join(ERROR_DIR, f"geekdo_product_{gameId}.txt")

    # Skip already processed or failed
    if os.path.exists(output_csv) or os.path.exists(output_json) or os.path.exists(error_file):
        print(f"⏩ Skipping game ID {gameId} (already processed)")
        continue

    print(f"\n🎯 Fetching game ID: {gameId}")

    start_time = time.time()
    all_products = []
    page = 1

    while True:

        try:
            url = base_url.format(gameId=gameId, page=page)
            print(f"📄 Fetching page {page}...")

            response = requests.get(url, timeout=15)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            try:
                data = response.json()
            except json.JSONDecodeError:
                raise Exception("Invalid JSON")

            products = data.get("products")

            # No products → natural end
            if not products:
                print("🚫 No more products found — stopping.")
                break

            # ----------------------------------------------
            # PROCESS PRODUCTS
            # ----------------------------------------------
            for product in products:
                flat = {}

                # simple fields
                for k, v in product.items():
                    if not isinstance(v, (dict, list)):
                        flat[k] = v

                # version info
                version = product.get("version") or {}
                flat["version_name"] = version.get("name")

                # object link
                obj = product.get("objectlink") or {}
                flat["game_name"] = obj.get("name")

                all_products.append(flat)

            print(f"✅ Retrieved {len(products)} products from page {page}")
            page += 1
            time.sleep(2)
       
        except Exception as e:
            # Save raw response for debugging
            raw_json_path = os.path.join(
                ERROR_DIR, f"geekdo_product_{gameId}_page_{page}_raw.json"
            )
            try:
                with open(raw_json_path, "w", encoding="utf-8") as jf:
                    jf.write(response.text if 'response' in locals() else "")
                print(f"📝 Saved raw error JSON → {raw_json_path}")
            except:
                print("⚠️ Could not save raw JSON.")

            # Log the error
            with open(error_file, "a", encoding="utf-8") as ef:
                ef.write(f"Page {page} error: {str(e)}\n")

            print(f"❌ Error on page {page}: {e} — skipping page and continuing.")
            page += 1
            time.sleep(1)
            continue
    

    # ===================================================
    # SAVE DATA (even partial)
    # ===================================================
    if all_products:
        df = pd.DataFrame(all_products)
        df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"💾 Saved CSV → {output_csv}")

        with open(output_json, "w", encoding="utf-8") as jf:
            json.dump(all_products, jf, ensure_ascii=False, indent=2)
        print(f"💾 Saved JSON → {output_json}")
    else:
        print("❌ No products collected at all.")
        with open(error_file, "a", encoding="utf-8") as ef:
            ef.write("No product data collected.\n")

    # ===================================================
    # UPDATE RUNTIME LOG
    # ===================================================
    runtime_sec = round(time.time() - start_time, 2)
    total_runtime += runtime_sec

    with open(RUNTIME_FILE, "a", encoding="utf-8") as rf:
        rf.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Game {gameId} runtime: {runtime_sec}s | Total: {round(total_runtime, 2)}s\n"
        )

    print(f"🕒 Game {gameId} took {runtime_sec:.2f}s (Total: {total_runtime:.2f}s)")
    time.sleep(1)



# specify the directory with your CSV files
directory = "./geekdo_products_csv/"

# get all CSV filenames
csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]

# read and combine them
dfs = []
for f in tqdm(csv_files, desc="Fetching games", unit="game"):
    file_path = os.path.join(directory, f)
    dfs.append(pd.read_csv(file_path))

# concatenate all DataFrames
combined_df = pd.concat(dfs, ignore_index=True)

# save to one CSV
combined_df.to_csv("products.csv", index=False)

print(f"✅ Combined {len(csv_files)} CSV files into products.csv")
