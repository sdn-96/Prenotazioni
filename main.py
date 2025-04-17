from ftpserver import FtpHandler
from web import login, request_data, analize 
from datetime import datetime
from deepdiff import DeepDiff
import json
import os
from config import BASE_FILENAME, DATA_FOLDER, DATE_FORMAT
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
    # Step 7: Salvataggio JSON
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_name = f"{BASE_FILENAME}_{timestamp}.json"  # Aggiungi il timestamp al nome del file
    file_path = f"{DATA_FOLDER}/{file_name}"
    json_data = {
        'columns': headers,
        'rows': data
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)  # `ensure_ascii=False` per caratteri speciali
    print(f"Dati salvati con successo in {file_name}")
    return file_name


if __name__=='__main__':
    timestamp = get_timestamp()
    session = login()
    results = request_data(session)
    print('dati ottenuti')
    headers, data_rows = analize(results)
    print('File analizzato')
    new_filename = save_to_json(headers, data_rows)
    print(f"{len(data_rows)} righe salvate in '{new_filename}'")

    # === FTP: Upload con confronto ===
    ftp_handler = FtpHandler()
    # Scarica il file JSON esistente (se presente)
    previous_content, previous_filename = ftp_handler.get_last_json() or (None, None)
    new_json_path = f"{DATA_FOLDER}/{new_filename}"
    with open(new_json_path, 'r', encoding='utf-8') as f:
        local_json_content = f.read()
    diff = DeepDiff(previous_content, local_json_content, ignore_order=True)
    if not diff:
        ftp_handler.rename(previous_filename, new_filename)
        print(f"🔁 Nessuna differenza: sovrascritto '{previous_filename}' con '{new_filename}'")
    else:
        # Carica un nuovo file con timestamp
        json_file_names = ftp_handler.get_files_from_ftp()
        jsons = ftp_handler.download_all()
        log = create_log(json_file_names, jsons)
        with open('storico_modifiche.txt', 'a') as f:
            f.write(log)
        ftp_handler.upload(new_json_path, new_filename)
        ftp_handler.upload('storico_modifiche.txt', 'storico_modifiche.txt')
    ftp_handler.quit()


