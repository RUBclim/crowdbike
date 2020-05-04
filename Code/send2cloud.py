import argparse
import json
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(
    prog='send2cloud',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    '-v', '--verbose',
    help='increase verbosity',
    action='store_true',
)
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
archive_dir = os.path.join(log_dir, 'archive')
folder_token = config['cloud']['folder_token']
passwd = config['cloud']['passwd']
base_url = config['cloud']['base_url']

# create archive directory
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

# check if there are files to upload
files_present = False
for element in os.listdir(log_dir):
    if os.path.isfile(os.path.join(log_dir, element)):
        files_present = True
        break

# pass verbose to curl or not?
if args.verbose:
    first_args = '-vT'
else:
    first_args = '-T'

if files_present:
    for log in os.listdir(log_dir):
        if os.path.splitext(log)[1].lower() == '.csv':
            print(f'uploading: {log} to the cloud')
            curl_call = f'curl {first_args} {os.path.join(log_dir, log)} -u {folder_token}:{passwd} -H X-Requested-With:XMLHttpRequest {base_url}/public.php/webdav/{log}'  # noqa E501
            curl_call = curl_call.split(' ')
            if args.verbose:
                subprocess.check_output(curl_call)
            else:
                subprocess.call(curl_call)
            shutil.move(os.path.join(log_dir, log), archive_dir)
elif not files_present:
    print(f'Everything up to date. There are no files to upload in "{log_dir}"')  # noqa E501
else:
    raise Exception(f'An unknown error occurred. {files_present} is not a boolean')  # noqa E501
