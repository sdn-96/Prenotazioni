import io
from ftplib import FTP
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR

# === FUNZIONE: Scarica ultimo file dal server ===
def get_last_json(ftp):
    files = ftp.nlst()
    json_files = sorted([f for f in files if f.endswith('.json')], reverse=True)
    if not json_files:
        return None

    latest_file = json_files[0]
    buffer = io.BytesIO()
    ftp.retrbinary(f"RETR {latest_file}", buffer.write)
    json_bytes = buffer.getvalue()
    try:
        json_text = json_bytes.decode('utf-8')  # Proviamo con utf-8
    except UnicodeDecodeError:
        print("⚠️ Il file remoto non è in UTF-8. Provo con latin-1...")
        json_text = json_bytes.decode('latin-1')
    return json_text, latest_file

def init_ftp():
    ftp = FTP(FTP_HOST, encoding='latin-1', timeout=100)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(FTP_DIR)
    return ftp

# === Funzione per scaricare i file dal server FTP ===
def get_files_from_ftp(ftp):
    files = ftp.nlst()  # Ottieni l'elenco dei file nella directory
    json_files = sorted([f for f in files if f.endswith('.json')], reverse=False)
    return json_files

