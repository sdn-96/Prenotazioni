from compare import get_changes, changes_to_json, integrate_changes
from ftpserver import FtpHandler
import json

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

        ftp_handler.upload_changes(json_change, change_filename)

        prev_json_str = next_json_str

def trial_rebuild():
    ftp_handler = FtpHandler()
    names = ftp_handler.list_jsons()
    prev_name = names[-2]
    last_name = names[-1]

    prev_json = ftp_handler.download(prev_name)
    last_json = ftp_handler.download(last_name)
    
    change_names = ftp_handler.list_changes()
    last_change = change_names[-1]
    last_change = ftp_handler.download_change(last_change)

    computed_json_dict = integrate_changes(prev_json, last_change)
    computed_json_str = json.dumps(computed_json_dict, indent=4)

    if computed_json_str == last_json:
        print('Il file è stato ricostruito correttamente')
    else:
        print('Il file ricostruito non è compatibile')


if __name__=='__main__':
    #fix()
    trial_rebuild()
