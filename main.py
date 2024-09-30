import requests
import json
import csv
from datetime import datetime
import os
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
import asyncio
from contextlib import asynccontextmanager
import pytz 

CSV_FILE = '/app/data/attraction_data.csv'
if os.getenv('ENV') != 'production':
    CSV_FILE = 'attraction_data.csv'

@asynccontextmanager
async def lifespan(app: FastAPI):
    scrape_task = asyncio.create_task(scrape_data())
    yield
    scrape_task.cancel()
    try:
        await scrape_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

def fetch_data():
    url = 'https://www.kierunekzator.pl/wp-admin/admin-ajax.php'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en,pl;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'pll_language=pl; _ga=GA1.1.1502138991.1727559077; _ga_03540X6BKY=GS1.1.1727618755.3.1.1727629558.0.0.0',
        'origin': 'https://www.kierunekzator.pl',
        'referer': 'https://www.kierunekzator.pl/czas-oczekiwania-na-atrakcje/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    data = {
        'action': 'wpda_datatables',
        'wpnonce': '7c4595a35f',
        'pubid': '1',
        'filter_field_name': '',
        'filter_field_value': '',
        'nl2br': ''
    }

    response = requests.post(url, headers=headers, data=data)
    return json.loads(response.text)

def process_data(data):
    warsaw_tz = pytz.timezone('Europe/Warsaw')
    timestamp = datetime.now(warsaw_tz).strftime("%Y-%m-%d %H:%M:%S")
    processed_data = [timestamp]
    for attraction in data['data']:
        if attraction[2] == "Czynna":
            processed_data.append(attraction[1])
        else:
            processed_data.append('-')
    return processed_data if any(value != '-' for value in processed_data[1:]) else None

def append_to_csv(data, filename='attraction_data.csv'):
    file_exists = os.path.isfile(filename)
    
    processed_data = process_data(data)
    if processed_data is None:
        print("No active attractions. Skipping this record.")
        return
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            headers = ['Timestamp'] + [attraction[0] for attraction in data['data'] if attraction[2] == "Czynna"]
            writer.writerow(headers)
        
        writer.writerow(processed_data)

@app.get("/energylandia-csv")
async def download_csv():
    if os.path.exists(CSV_FILE):
        return FileResponse(CSV_FILE, media_type='text/csv', filename='attraction_data.csv')
    return Response(content="CSV file not found", status_code=404)

async def scrape_data():
    while True:
        try:
            data = fetch_data()
            append_to_csv(data, filename=CSV_FILE)
            print(f"Data appended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        await asyncio.sleep(15 * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)