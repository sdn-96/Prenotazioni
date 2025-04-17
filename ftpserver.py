import io, json
from ftplib import FTP
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR

class FtpHandler():
    def __init__(self):
        self.ftp = FTP(FTP_HOST, encoding='latin-1', timeout=100)
        self.ftp.login(FTP_USER, FTP_PASS)
        self.ftp.cwd(FTP_DIR)

    # === Funzione per scaricare i file dal server FTP ===
    def list(self):
        files = self.ftp.nlst()  # Ottieni l'elenco dei file nella directory
        json_files = sorted([f for f in files if f.endswith('.json')], reverse=False)
        return json_files

    # === FUNZIONE: Scarica ultimo file dal server ===
    def get_last_json(self):
        latest_file = self.list()[-1]
        json_text = self.download(latest_file)
        return json_text, latest_file

    def rename(self, oldname, newname):
        self.ftp.rename(oldname, newname)

    def upload(self, path, filename):
        with open(path, 'rb') as f:
            self.ftp.storbinary(f"STOR {filename}", f)
            print(f"📤 Nuovo file caricato: {filename}")

        # === Funzione per scaricare un file JSON dal server FTP ===
    def download(self, filename):
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
            
    def download_all(self):
        file_names = self.list()
        return [self.download(filename) for filename in file_names]

    def quit(self):
        self.ftp.quit()

