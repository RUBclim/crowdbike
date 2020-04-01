import argparse
import json
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('config_path', help='path to "config.json" file', type=str)
parser.add_argument('-v', help='increase verbosity', action='store_true')
args = parser.parse_args()

with open(args.config_path, 'r') as config:
    config = json.load(config)

log_dir = config['user']['logfile_path']
folder_token = config['cloud']['folder_token']
passwd = config['cloud']['passwd']
base_url = config['cloud']['base_url']

if args.v:
    first_args = '-vT'
else:
    first_args = '-T'

for log in os.listdir(log_dir):
    if os.path.splitext(log)[1].lower() == '.csv':
        print(f'uploading: {log} to the cloud')
        curl_call = f'curl {first_args} {os.path.join(log_dir, log)} -u {folder_token}:{passwd} -H X-Requested-With:XMLHttpRequest {base_url}/public.php/webdav/{log}'  # noqa 501
        curl_call = curl_call.split(' ')
        if args.v:
            subprocess.check_output(curl_call)
        else:
            subprocess.call(curl_call)
