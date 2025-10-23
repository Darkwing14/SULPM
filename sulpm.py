#!/usr/bin/env python3
# SULPM - Small Universal Linux Package Manager
# This file is only here to open-source the project and make SULPM able to update itself.

import os
import sys
import json

pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"

def download(url, location, sudo=True):
    prefix = 'sudo ' if sudo else ''
    if os.system(f'{prefix}curl -fsSL "{url}" -o "{location}"') != 0:
        print(f'(!) SULPM: failure: could not download {url}.')
        sys.exit(1)

def fetch_metadata(filename):
    temp = '~/.tempdownloadsulpm'
    download(BASE_URL + filename, temp, sudo=False)
    with open(temp, 'r') as f:
        content = f.read()
    os.remove(temp)
    return content

# --------------------------------------------------
# REMOVE MODE
# --------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1].lower() == 'remove':
    if len(sys.argv) < 3:
        print("(!) SULPM: usage: sulpm remove <package>")
        sys.exit(1)

    packages_to_remove = sys.argv[2:]
    if not os.path.exists('.sulpmlog'):
        print("(!) SULPM: No log file found — nothing to remove.")
        sys.exit(0)

    with open('~/.sulpmlog', 'r') as f:
        lines = f.read().splitlines()

    new_lines = []
    removed_any = False

    i = 0
    while i < len(lines):
        if i + 1 >= len(lines):
            break
        name = lines[i]
        meta = json.loads(lines[i + 1])

        if name in packages_to_remove:
            print(f'(i) SULPM: Removing {name}')
            for file in meta:
                path = file
                if path.startswith('#'):
                    path = os.path.join('/usr/bin/', path[1:])
                elif path.startswith('~'):
                    path = os.path.expanduser(path)
                try:
                    os.remove(path)
                    print(f'(✓) Deleted {path}')
                except FileNotFoundError:
                    print(f'(!) Skipped missing file {path}')
                except Exception as e:
                    print(f'(!) Could not delete {path}: {e}')
            removed_any = True
        else:
            new_lines.append(lines[i])
            new_lines.append(lines[i + 1])
        i += 2

    with open('~/.sulpmlog', 'w') as f:
        f.write('\n'.join(new_lines) + '\n')

    if removed_any:
        print('(SUCCESS) SULPM: removal complete.')
    else:
        print('(!) SULPM: no matching packages found.')
    sys.exit(0)
# --------------------------------------------------

# Normal install mode
BASE_URL = 'https://raw.githubusercontent.com/Darkwing14/SULPM/main/'
if len(sys.argv) > 3:
    BASE_URL = f'https://raw.githubusercontent.com/{sys.argv[2]}/{sys.argv[3]}/main/'
package_name = sys.argv[1]

executable_folder = '/usr/bin/'
print('(i) SULPM: Init.')

print('(i) SULPM: Downloading metadata.')
JSON = json.loads(fetch_metadata(package_name + '.sulpm'))
Meta = {}

local = input('(Y/N) SULPM: Install locally? (Type yes if you want to avoid using sudo.)\n'
              'Not all programs may support this; if this errors, try saying no.\n> ').lower().startswith('y') # local means 'Am I trying to avoid sudo/install in home?'

print('(i) SULPM: Preparing to unpack.')

for file in JSON:
    value = JSON[file]

    if not isinstance(value, str) or not value.strip():
        Meta[file] = value
        continue

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

    if handle == 'executable':
        try:
            if local:
                os.chmod(filename, os.stat(filename).st_mode | 0o111)
            else:
                os.system(f'sudo chmod +x {filename}')
        except Exception as e:
            print(f'(!) SULPM: could not set executable bit for {filename}: {e}')

    if handle == 'meta':
        Meta[file] = JSON[file]

with open('~/.sulpmlog', 'a') as f:
    f.write(package_name + '\n' + json.dumps(Meta) + '\n')

print('(SUCCESS) SULPM')
