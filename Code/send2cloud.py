import argparse
import json
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-v', help='increase verbosity', action='store_true')
args = parser.parse_args()

# __load config files__
with open(
    os.path.join(
        os.path.dirname(__file__),
        'config.json',
    ), 'r',
) as config:
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
