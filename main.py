from ftpserver import FtpHandler
from web import login, request_data, analize 
from datetime import datetime
from deepdiff import DeepDiff
import json
import os
from config import BASE_FILENAME, DATE_FORMAT
from compare import create_log
import requests

def get_timestamp():
    try:
        # Fetch UTC time from WorldTimeAPI
        response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
        utc_time = response.json()["utc_datetime"]
        now = datetime.fromisoformat(utc_time)
    except Exception:
        now = datetime.now()
    finally:
        timestamp = now.strftime(DATE_FORMAT)
    return timestamp
    
def save_to_json(headers, data):
    json_data = {
        'columns': headers,
        'rows': data
    }
    json_str = json.dumps(json_data, indent=4)
    return json_str


if __name__=='__main__':
    timestamp = get_timestamp()
    new_filename = f"{BASE_FILENAME}_{timestamp}.json" 
    session = login()
    results = request_data(session)
    print('dati ottenuti')
    headers, data_rows = analize(results)
    print('File analizzato')
    new_json_str = save_to_json(headers, data_rows)
    print(f"{len(data_rows)} righe salvate in '{new_filename}'")

    ftp_handler = FtpHandler()
    # Scarica il file JSON esistente (se presente)
    last_json_str, previous_filename = ftp_handler.get_last_json() or (None, None)
    diff = DeepDiff(last_json_str, new_json_str, ignore_order=True)
    if not diff:
        ftp_handler.rename(previous_filename, new_filename)
        print(f"🔁 Nessuna differenza: sovrascritto '{previous_filename}' con '{new_filename}'")
    else:
        # Carica un nuovo file con timestamp
        json_file_names = ftp_handler.list()
        jsons = ftp_handler.download_all()
        log = create_log(json_file_names, jsons)
        with open('storico_modifiche.txt', 'a') as f:
            f.write(log)
        ftp_handler.upload(new_json_str, new_filename)
        ftp_handler.upload('storico_modifiche.txt', 'storico_modifiche.txt')
    ftp_handler.quit()


