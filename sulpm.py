#!/usr/bin/env python3
# SULPM - Small Universal Linux Package Manager
# This file is only here to open-source the project and make SULPM able to update itself.

import os
import sys
import json

pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"

BASE_URL = 'https://raw.githubusercontent.com/Darkwing14/SULPM/main/'
if len(sys.argv) > 3:
    BASE_URL = f'https://raw.githubusercontent.com/{sys.argv[2]}/{sys.argv[3]}/main/'
package_name = sys.argv[1]

executable_folder = '/usr/bin/'
print('(i) SULPM: Init.')

def download(url, location, sudo=True):
    prefix = 'sudo ' if sudo else ''
    if os.system(f'{prefix}curl -fsSL "{url}" -o "{location}"') != 0:
        print(f'(!) SULPM: failure: could not download {url}.')
        sys.exit(1)

def fetch_metadata(filename):
    temp = '.tempdownloadsulpm'
    download(BASE_URL + filename, temp, sudo=False)
    with open(temp, 'r') as f:
        content = f.read()
    os.remove(temp)
    return content

print('(i) SULPM: Downloading metadata.')
JSON = json.loads(fetch_metadata(package_name + '.sulpm'))
Meta = {}

local = input('(Y/N) SULPM: Install locally? (Type yes if you want to avoid using sudo.)\n'
              'Not all programs may support this; if this errors, try saying no.\n> ').lower().startswith('y')

print('(i) SULPM: Preparing to unpack.')

for file in JSON:
    value = JSON[file]

    # Skip metadata or malformed entries
    if not isinstance(value, str) or not value.strip():
        Meta[file] = value
        continue

    # Automatically prepend BASE_URL if not a full URL
    if not value.startswith('http://') and not value.startswith('https://'):
        value = BASE_URL + value

    handle = 'meta'
    filename = file

    if file.startswith('/'):
        handle = 'root'
    elif file.startswith('~'):
        handle = 'home'
        filename = os.path.expanduser(file)
    elif file.startswith('#'):
        handle = 'executable'
        executable_folder = os.path.expanduser('~/.local/bin/') if local else '/usr/bin/'
        filename = os.path.join(executable_folder, file[1:])

    dirpath = os.path.dirname(filename)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
        
    filename = filename.replace('python3.x', pyver)

    print(f'(i) SULPM: Unpacking {filename}')
    sudo = (handle == 'root' or (handle == 'executable' and not local))
    if not handle == 'meta':
        download(value, filename, sudo)

    # Make executables actually executable
    if handle == 'executable':
        try:
            os.chmod(filename, os.stat(filename).st_mode | 0o111)
        except Exception as e:
            print(f'(!) SULPM: could not set executable bit for {filename}: {e}')

    # Log metadata
    if handle == 'meta':
        Meta[file] = JSON[file]

with open('.sulpmlog', 'a') as f:
    f.write(package_name + '\n' + json.dumps(Meta) + '\n')

print('(SUCCESS) SULPM')

