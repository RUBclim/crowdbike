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

# load config files
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
if not base_url[-1] == '/':
    base_url += '/'

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
            curl_call = f'curl {first_args} {os.path.join(log_dir, log)} -u '\
                f'{folder_token}:{passwd} -H X-Requested-With:XMLHttpRequest '\
                f'{base_url}public.php/webdav/{log}'

            # create argument list to pass to the subprocess call
            curl_call = curl_call.split(' ')

            if args.verbose:
                call = subprocess.run(args=curl_call, capture_output=True)
                stdoutput = call.stdout.decode('utf-8')
                print(call.stderr.decode('utf-8'))
                if stdoutput == '':
                    shutil.move(os.path.join(log_dir, log), archive_dir)
                else:
                    print(' error '.center(79, '='))
                    print(stdoutput)

            else:
                call = subprocess.run(args=curl_call, capture_output=True)
                stdoutput = call.stdout.decode('utf-8')

                if stdoutput == '':
                    shutil.move(os.path.join(log_dir, log), archive_dir)
                else:
                    print(' error '.center(79, '='))
                    print(stdoutput)

elif not files_present:
    print(f'Everything up to date. There are no files to upload in "{log_dir}"')  # noqa E501
else:
    raise Exception(f'An unknown error occurred. {files_present} is not a boolean')  # noqa E501
