from compare import get_changes, changes_to_json
from ftpserver import FtpHandler

def fix():
    ftp_handler = FtpHandler()
    names = ftp_handler.list_jsons()
    prev_name = names[0]
    prev_json_str = ftp_handler.download(prev_name)
    for i in range(len(names)-1):
        next_name = names[i+1]
        next_json_str = ftp_handler.download(next_name)

        tmp1 = prev_name.split('_')[-1].replace('.json', '')
        tmp2 = next_name.split('_')[-1].replace('.json', '')

        change_list = get_changes(prev_json_str, next_json_str)
        json_change = changes_to_json(change_list)
        change_filename = f'{tmp1}_{tmp2}.json'

        ftp_handler.ftp.cwd('CHANGES')
        ftp_handler.upload(json_change, change_filename)
        ftp_handler.ftp.cwd('..')

        prev_json_str = next_json_str

if __name__=='__main__':
    fix()
