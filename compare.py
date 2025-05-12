import os
import io
import json
from ftpserver import FtpHandler
from datetime import datetime
from config import DATE_FORMAT
import copy

LOG_FILE = 'storico_modifiche.txt'

ALL_PARAMS = [ "Appartamento", "Nome", "Nazione", "Check in", "Check out", "Notti", "Totale pernottamento", "Tot proprietario", "Netto proprietario", ""]
# Colonne da confrontare
COMPARE_PARAMS = ["Check in", "Check out", "Notti", "Totale pernottamento", "Tot proprietario", "Netto proprietario"]

# Costruisce un dizionario {Nome: riga} per ogni file
def build_row_dict(data):
    col_idx = {col: i for i, col in enumerate(data["columns"])}
    nome_idx = col_idx["Nome"]
    return {
        row[nome_idx]: row
        for row in data["rows"]
    }, col_idx

def compare_jsons(old_json_str, new_json_str):
    old_json = json.loads(old_json_str)
    new_json = json.loads(new_json_str)
    old_dict, old_cols = build_row_dict(old_json)
    new_dict, new_cols = build_row_dict(new_json)

    changes = []

    # Prenotazioni cancellate
    for nome in old_dict:
        if nome not in new_dict:
            row = old_dict[nome]
            changes.append(f"❌ Prenotazione cancellata: {row[0]} - {nome}, {row[3]} -> {row[4]}, -{row[8]}")

    # Prenotazioni nuove o modificate
    for nome in new_dict:
        if nome not in old_dict:
            row = new_dict[nome]
            changes.append(f"✅ Nuova prenotazione: {row[0]} - {nome}, {row[3]} -> {row[4]}, +{row[8]}")
        else:
            diffs = []
            old_row = old_dict[nome]
            new_row = new_dict[nome]
            for param in COMPARE_PARAMS:
                idx = old_cols[param]
                old_val = str(old_row[idx])
                new_val = str(new_row[idx])
                if old_val != new_val:
                    diffs.append(f"{param}: '{old_val}' -> '{new_val}'")
            if diffs:
                changes.append(f"🔄 Modifiche in {nome}: " + "; ".join(diffs))
    return changes

def readable_date(timestamp):
    data_file = datetime.strptime(timestamp, DATE_FORMAT)
    return datetime.strftime(data_file, "%d/%m/%Y %H:%M")

#####################################################################################

def create_log(json_file_names, json_files):
    timestamps = [file.split('_')[-1].replace('.json', '') for file in json_file_names]
    res = ""
    res += "📘 STORICO MODIFICHE PRENOTAZIONI\n\n"
    res += f"Rilevazione Base {readable_date(timestamps[0])}"+"\n"
    res += "="*40 + "\n\n"
    for i in range(1, len(json_file_names)):
        file1 = json_file_names[i - 1]
        file2 = json_file_names[i]
        old_json = json_files[i-1]
        new_json = json_files[i]

        timestamp1 = timestamps[i-1]
        timestamp2 = timestamps[i]

        print(f"Confrontando {file1} con {file2}...")

        changes = compare_jsons(old_json, new_json)
        res += f"Rilevazione {readable_date(timestamp2)}"+"\n\n"
        for change in changes:
            if change:
                res += "• " + change + "\n"
            else:
                res += "✅ Nessuna modifica rilevata\n"
        res += "\n" + "-"*40 + "\n\n"
    return res

def create_log_from_changes(json_changes_names, json_changes, reverse=True):
    res = ""
    res += "📘 STORICO MODIFICHE PRENOTAZIONI\n\n"
    #res += f"Rilevazione Base {readable_date(timestamps[0])}"+"\n"
    res += "="*40 + "\n\n"
    if reverse:
        iteration_list = range(len(json_changes)-1, -1, -1)
    else:
        iteration_list = range(len(json_changes)-1, -1, -1)
    for i in iteration_list:
        _dict = json.loads(json_changes[i])
        if _dict["type"] != "change":
            raise Exception('There is a non change file')
        name = json_changes_names[i].replace('.json', '')
        timestamp = name.split('_')[-1]
        res += f"Rilevazione {readable_date(timestamp)}"+"\n\n"
        for row in _dict["rows"]:
            if row[0]=='added':
                res += f"✅ Nuova prenotazione: {row[1]} - {row[2]}, {row[4]} -> {row[5]}, +{row[9]}"
            if row[0]=='removed':
                res += f"❌ Prenotazione cancellata: {row[1]} - {row[2]}, {row[4]} -> {row[5]}, -{row[9]}"
            if row[0]=='modified':
                res += f"🔄 Modifiche in: {row[1]} - {row[2]}, {row[4]} -> {row[5]}, {row[9]}"
            res += '\n'
        res += "\n" + "-"*40 + "\n\n"

    return res






    

##########################################################

def get_changes(json1, json2):
    old_json = json.loads(json1)
    new_json = json.loads(json2)
    old_dict, old_cols = build_row_dict(old_json)
    new_dict, new_cols = build_row_dict(new_json)

    changes = []

    # Prenotazioni cancellate
    for nome in old_dict:
        if nome not in new_dict:
            change = ["removed"] + old_dict[nome]
            changes.append(change)

    # Prenotazioni nuove o modificate
    for nome in new_dict:
        if nome not in old_dict:
            change = ["added"] + new_dict[nome]
            changes.append(change)
        else:
            diffs = []
            old_row = old_dict[nome]
            new_row = new_dict[nome]
            for param in ALL_PARAMS:
                idx = old_cols[param]
                old_val = str(old_row[idx])
                new_val = str(new_row[idx])
                if old_val != new_val:
                    diffs.append(f"{param}: '{old_val}' -> '{new_val}'")
            if diffs:
                change = ["modified"] + new_row
                changes.append(change)
    return changes

def changes_to_json(changes):
    _dict = {
        "type": "change",
        "columns": ["Change"]+ALL_PARAMS,
        "rows" : changes
    }
    return json.dumps(_dict, indent=4)

#####################################################

def integrate_changes(base_json_str, changes_json_str):
    base_json = json.loads(base_json_str)
    change_json = json.loads(changes_json_str)
    #base_dict, base_cols = build_row_dict(base_json)
    #change_dict, change_cols = build_row_dict(change_json)
    changes = change_json["rows"]
    new_dict = base_json
    for change in changes:
        change_type = change[0]
        change_row = change[1:]
        if change_type == "added":
            new_dict["rows"].append(change_row)
        elif change_type == "removed":
            removed_reservation = change_row[1]
            new_dict["rows"] = [_row for _row in new_dict["rows"] if _row[1] != removed_reservation]
        elif change_type == "modified":
            changed_reservation = change_row[1]
            new_dict["rows"] = [
                _row if _row[1] != changed_reservation else change_row
                for _row in new_dict["rows"]
                ]
    return new_dict
    

if __name__=='__main__':
    ftp_handler = FtpHandler()
    json_file_names = ftp_handler.list_jsons()
    timestamps = [file.split('_')[-1].replace('.json', '') for file in json_file_names]
    if len(json_file_names) >= 2:
        jsons = ftp_handler.download_all()
        log = create_log(json_file_names, jsons)
        ftp_handler.upload(log, 'storico_modifiche.txt')
    ftp_handler.quit()
