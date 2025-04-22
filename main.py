from ftpserver import FtpHandler
from web import login, request_data, analize 
from datetime import datetime
from deepdiff import DeepDiff
import json
import os
import sys
from config import BASE_FILENAME, DATE_FORMAT
from compare import create_log
import requests

def get_timestamp():
    try:
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
    if len(sys.argv)>1:
        force_new_log = sys.argv[1]=='force'
    else:
        force_new_log = False
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
    last_json_str, previous_filename = ftp_handler.get_last_json() or (None, None)
    diff = DeepDiff(last_json_str, new_json_str, ignore_order=True)
    if diff:
        ftp_handler.upload(new_json_str, new_filename)
    else:
        ftp_handler.rename(previous_filename, new_filename)
        print(f"🔁 Nessuna differenza: sovrascritto '{previous_filename}' con '{new_filename}'")

    if diff or ('storico_modifiche.txt' not in ftp_handler.list()) or force_new_log:
        jsons = ftp_handler.download_all()
        json_file_names = ftp_handler.list_jsons()
        log = create_log(json_file_names, jsons)
        ftp_handler.upload(log, 'storico_modifiche.txt')
    ftp_handler.quit()


