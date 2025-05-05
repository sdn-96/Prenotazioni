import io, json
from ftplib import FTP
from config import FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR

class FtpHandler():
    def __init__(self):
        self.ftp = FTP(FTP_HOST, encoding='latin-1', timeout=100)
        self.ftp.login(FTP_USER, FTP_PASS)
        self.ftp.cwd(FTP_DIR)

    def list(self):
        return sorted(self.ftp.nlst())

    def list_jsons(self):
        files = self.ftp.nlst()  # Ottieni l'elenco dei file nella directory
        json_files = sorted([f for f in files if f.endswith('.json')], reverse=False)
        return json_files

    def get_last_json(self):
        latest_file = self.list_jsons()[-1]
        json_text = self.download(latest_file)
        return json_text, latest_file

    def rename(self, oldname, newname):
        self.ftp.rename(oldname, newname)

    def upload_file(self, path, filename):
        with open(path, 'rb') as f:
            self.ftp.storbinary(f"STOR {filename}", f)
            print(f"📤 Nuovo file caricato: {filename}")

    def upload(self, json_str, filename):
        json_bytes = json_str.encode('utf-8')
        buffer = io.BytesIO(json_bytes)
        buffer.seek(0)
        self.ftp.storbinary(f"STOR {filename}", buffer)
        print(f"📤 Nuovo file caricato: {filename}")

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
            return json_text
            
    def download_all(self):
        file_names = self.list_jsons()
        return [self.download(filename) for filename in file_names]

    def quit(self):
        self.ftp.quit()

    def fix_jsons(self):
        names = self.list_jsons()
        for name in names:
            text = self.download(name)
            new_text = text.encode('ascii', 'ignore').decode()
            clean_dictionary = self.strip_all_strings(json.loads(new_text)) 
            new_text = json.dumps(clean_dictionary, indent=4)
            self.upload(new_text, name)

    def strip_all_strings(self, obj):
        if isinstance(obj, str):
            return obj.strip()
        elif isinstance(obj, dict):
            return {self.strip_all_strings(k): self.strip_all_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.strip_all_strings(elem) for elem in obj]
        else:
            raise Exception(f'Wrong type of data: {type(obj)}')
            
if __name__=='__main__':
    ftp_handler = FtpHandler()
    ftp_handler.fix_jsons()
