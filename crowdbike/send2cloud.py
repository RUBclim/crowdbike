import argparse
import json
import os
import shutil
import subprocess

from crowdbike.helpers import CONFIG_DIR


def main() -> int:
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
    with open(os.path.join(CONFIG_DIR, 'config.json')) as cfg:
        config = json.load(cfg)

    log_dir = config['user']['logfile_path']
    archive_dir = os.path.join(log_dir, 'archive')
    folder_token = config['cloud']['folder_token']
    passwd = config['cloud']['passwd']
    base_url = config['cloud']['base_url']
    if not base_url[-1] == '/':
        base_url += '/'

    # create archive directory
    os.makedirs(archive_dir, exist_ok=True)

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
                curl_call = [
                    'curl', first_args, os.path.join(log_dir, log), '-u',
                    f'{folder_token}:{passwd}', '-H',
                    'X-Requested-With:XMLHttpRequest',
                    f'{base_url}public.php/webdav/{log}',
                ]

                if args.verbose:
                    call = subprocess.run(args=curl_call, capture_output=True)
                    stdoutput = call.stdout.decode('utf-8')
                    stderr = call.stderr.decode('utf-8')
                    print(stderr)
                    err = stderr.split('curl:')

                    if len(err) > 1:
                        err_str = err[1]

                    if stdoutput == '' and len(err) == 1:
                        shutil.move(os.path.join(log_dir, log), archive_dir)
                    else:
                        print(' error '.center(79, '='))
                        print(stdoutput)
                        print(err)

                else:
                    call = subprocess.run(args=curl_call, capture_output=True)
                    stdoutput = call.stdout.decode('utf-8')
                    stderr = call.stderr.decode('utf-8')
                    err = stderr.split('curl:')

                    if len(err) > 1:
                        err_str = err[1]  # noqa F841

                    if stdoutput == '' and len(err) == 1:
                        shutil.move(os.path.join(log_dir, log), archive_dir)
                    else:
                        print(' error '.center(79, '='))
                        print(stdoutput)
                        print(err)

    elif not files_present:
        print(
            f'Everything up to date. '
            f'There are no files to upload in "{log_dir}"',
        )
    else:
        raise Exception(
            f'An unknown error occurred. {files_present} is not a boolean',
        )

    return 0


if __name__ == '__main__':
    exit(main())
