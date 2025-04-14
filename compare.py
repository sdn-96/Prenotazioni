import os
import io
import json
from ftpserver import init_ftp, get_files_from_ftp
from datetime import datetime
from config import DATE_FORMAT

LOG_FILE = 'storico_modifiche.txt'

# Colonne da confrontare
PARAMS = ["Check in", "Check out", "Notti", "Totale pernottamento", "Tot proprietario", "Netto proprietario"]


# === Funzione per caricare un file JSON dal server FTP ===
def load_json_from_ftp(ftp, filename):
    buffer = io.BytesIO()
    ftp.retrbinary(f"RETR {filename}", buffer.write)
    json_bytes = buffer.getvalue()
    json_text = json_bytes.decode('utf-8')
    return json.loads(json_text)

# Costruisce un dizionario {Nome: riga} per ogni file
def build_row_dict(data):
    col_idx = {col: i for i, col in enumerate(data["columns"])}
    nome_idx = col_idx["Nome"]
    return {
        row[nome_idx]: row
        for row in data["rows"]
    }, col_idx

# Confronta due file JSON e restituisce una lista di modifiche testuali
def compare_jsons(old_json, new_json):
    old_dict, old_cols = build_row_dict(old_json)
    new_dict, new_cols = build_row_dict(new_json)

    changes = []

    # Prenotazioni cancellate
    for nome in old_dict:
        if nome not in new_dict:
            changes.append(f"❌ Prenotazione cancellata: {nome}, -{old_dict[nome][8]}")

    # Prenotazioni nuove o modificate
    for nome in new_dict:
        if nome not in old_dict:
            changes.append(f"✅ Nuova prenotazione: {nome}, +{new_dict[nome][8]}")
        else:
            diffs = []
            old_row = old_dict[nome]
            new_row = new_dict[nome]
            for param in PARAMS:
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

def create_log(ftp):
    json_file_names = get_files_from_ftp(ftp)
    timestamps = [file.split('_')[-1].replace('.json', '') for file in json_file_names]
    res = ""
    res += "📘 STORICO MODIFICHE PRENOTAZIONI\n\n"
    res += f"Rilevazione Base {readable_date(timestamps[0])}"+"\n"
    res += "="*40 + "\n\n"
    for i in range(1, len(json_file_names)):
        # Carica i due file JSON da confrontare
        file1 = json_file_names[i - 1]
        file2 = json_file_names[i]

        print(f"Confrontando {file1} con {file2}...")

        # Carica il contenuto dei file JSON dal server FTP
        old_json = load_json_from_ftp(ftp, file1)
        new_json = load_json_from_ftp(ftp, file2)

        # Estrai i timestamp dai nomi dei file (assumendo che contengano il timestamp nel nome)
        timestamp1 = timestamps[i-1]
        timestamp2 = timestamps[i]

        # Confronta i due file e registra le modifiche
        changes = compare_jsons(old_json, new_json)
        res += f"Rilevazione {readable_date(timestamp2)}"+"\n\n"
        for change in changes:
            if change:
                res += "• " + change + "\n"
            else:
                res += "✅ Nessuna modifica rilevata\n"
        res += "\n" + "-"*40 + "\n\n"
    return res

def get_changes(json1, json2):
    old_dict, old_cols = build_row_dict(json1)
    new_dict, new_cols = build_row_dict(json2)

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
            for param in PARAMS:
                idx = old_cols[param]
                old_val = str(old_row[idx])
                new_val = str(new_row[idx])
                if old_val != new_val:
                    diffs.append(f"{param}: '{old_val}' -> '{new_val}'")
            if diffs:
                change = ["modified"] + new_row
                changes.append(change)
    return changes

def save_changes_to_json(changes, path):
    _dict = {
        "type": "change",
        "columns": ["Change"]+PARAMS,
        "rows" : changes
    }
    with open(path, "w") as f:
        json.dump(_dict, f, indent=4)
    return
    
    

if __name__=='__main__':
    # === MAIN ===
    ftp = init_ftp()

    # Ottenere l'elenco dei file JSON ordinati per timestamp (nome)
    json_files = get_files_from_ftp(ftp)
    timestamps = [file.split('_')[-1].replace('.json', '') for file in json_files]

    # Se ci sono almeno due file, confrontali
    if len(json_files) >= 2:
        storico_path = os.path.join(os.getcwd(), LOG_FILE)
        with open(storico_path, 'w', encoding='utf-8') as log:
            log.write("📘 STORICO MODIFICHE PRENOTAZIONI\n\n")
            log.write(f"Rilevazione Base {readable_date(timestamps[0])}"+"\n")
            log.write("="*40 + "\n\n")
            for i in range(1, len(json_files)):
                # Carica i due file JSON da confrontare
                file1 = json_files[i - 1]
                file2 = json_files[i]

                print(f"Confrontando {file1} con {file2}...")

                # Carica il contenuto dei file JSON dal server FTP
                old_json = load_json_from_ftp(ftp, file1)
                new_json = load_json_from_ftp(ftp, file2)

                # Estrai i timestamp dai nomi dei file (assumendo che contengano il timestamp nel nome)
                timestamp1 = timestamps[i-1]
                timestamp2 = timestamps[i]

                # Confronta i due file e registra le modifiche
                changes = compare_jsons(old_json, new_json)
                log.write(f"Rilevazione {readable_date(timestamp2)}"+"\n\n")
                for change in changes:
                    if change:
                        log.write("• " + change + "\n")
                    else:
                        log.write("✅ Nessuna modifica rilevata\n")
                log.write("\n" + "-"*40 + "\n\n")
    ftp.quit()


