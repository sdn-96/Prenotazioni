import io
from ftplib import FTP
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR

class FtpHandler()
    def __init__(self):
        self.ftp = FTP(FTP_HOST, encoding='latin-1', timeout=100)
        self.ftp.login(FTP_USER, FTP_PASS)
        self.ftp.cwd(FTP_DIR)

    # === Funzione per scaricare i file dal server FTP ===
    def get_files_from_ftp(self):
        files = self.ftp.nlst()  # Ottieni l'elenco dei file nella directory
        json_files = sorted([f for f in files if f.endswith('.json')], reverse=False)
        return json_files

    # === Funzione per scaricare un file JSON dal server FTP ===
    def load_json_from_ftp(self, filename):
        buffer = io.BytesIO()
        self.ftp.retrbinary(f"RETR {filename}", buffer.write)
        json_bytes = buffer.getvalue()
        try:
            json_text = json_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print("⚠️ Il file remoto non è in UTF-8. Provo con latin-1...")
            json_text = json_bytes.decode('latin-1')
        finally:
            return json.loads(json_text)

    # === FUNZIONE: Scarica ultimo file dal server ===
    def get_last_json(ftp):
        latest_file = self.ftp.get_files_from_ftp()
        json_text = self.ftp.load_json_from_ftp(latest_file)
        return json_text, latest_file

    def rename(self, oldname, newname):
        self.ftp.rename(oldname, newname)

    def upload(path, filename):
        with open(path, 'rb') as f:
            self.ftp.storbinary(f"STOR {new_filename}", f)
            print(f"📤 Nuovo file caricato: {new_filename}")

    def quit(self):
        self.ftp.quit()

