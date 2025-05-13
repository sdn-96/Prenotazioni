from ftpserver import FtpHandler
from web import login, request_data, analize 
from datetime import datetime, timedelta, timezone
from deepdiff import DeepDiff
import json
import os
from config import BASE_FILENAME, DATE_FORMAT
from compare import create_log, get_changes, create_log_from_changes, changes_to_json, integrate_changes
import requests

def to_isoformat(iso_str):
    if '.' in iso_str:
        date_part, frac = iso_str.split('.')
        frac = frac[:6]  # prendi solo i primi 6 decimali
        iso_str = f"{date_part}.{frac}"
    return iso_str 

def get_timestamp():
    try:
        url = "https://www.timeapi.io/api/Time/current/zone?timeZone=UTC"
        res = requests.get(url)
        print('Real time retrieved')
    except Exception:
        now_ita = datetime.now()
        print('Real time retriving failed')
    else:
        data = res.json()
        utc_iso_str = data["dateTime"]
        utc_iso_str = to_isoformat(utc_iso_str)
        now = datetime.fromisoformat(utc_iso_str)
        now = now.replace(tzinfo=timezone.utc)  # Assicura che sia UTC
        now_ita = now.astimezone(timezone(timedelta(hours=2)))
    finally:
        timestamp = now_ita.strftime(DATE_FORMAT)
        print(timestamp)
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

    ftp_handler = FtpHandler()
    json_names = ftp_handler.list_jsons()
    last_json_name = json_names[-1]
    last_json_str = ftp_handler.download(last_json_name)
    last_tmp = json_names[-1].split('_')[-1].replace('.json','')

    last_changes, totals = get_changes(last_json_str, new_json_str)
    changes_name = f'{last_tmp}_{timestamp}.json'

    if last_changes:
        changes_str = changes_to_json(last_changes, totals) 
        ftp_handler.upload_changes(changes_str, changes_name)
        ftp_handler.upload(new_json_str, new_filename)
        ftp_handler.delete(last_json_name)
    else:
        ftp_handler.rename(last_json_name, new_filename)
        print(f"🔁 Nessuna differenza: sovrascritto '{last_json_name}' con '{new_filename}'")

    all_json_changes = ftp_handler.download_all_changes()
    all_names_changes = ftp_handler.list_changes()
    log = create_log_from_changes(all_names_changes, all_json_changes, timestamp)
    ftp_handler.upload(log, 'storico_modifiche_prova.txt')
    ftp_handler.quit()


