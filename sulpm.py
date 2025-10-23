#!/usr/bin/env python3
# SULPM - Small Universal Linux Package Manager
# Fixed version: expand paths, record installed files in log, handle permissions and temp files.

import os
import sys
import json
import tempfile
import subprocess

def run(cmd):
    return subprocess.call(cmd, shell=True)

log_path = os.path.expanduser('~/.sulpmlog')

# ensure log exists
if not os.path.exists(log_path):
    open(log_path, 'w').close()

pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"

def download(url, location, sudo=True):
    prefix = 'sudo ' if sudo else ''
    dest_dir = os.path.dirname(location)
    if dest_dir:
        if sudo:
            # create dest dir with sudo if necessary
            run(f'{prefix}mkdir -p "{dest_dir}"')
        else:
            os.makedirs(dest_dir, exist_ok=True)

    rc = run(f'{prefix}curl -fsSL "{url}" -o "{location}"')
    if rc != 0:
        print(f'(!) SULPM: failure: could not download {url}.')
        sys.exit(1)

def fetch_metadata(filename):
    # use a proper temporary file and remove it after reading
    fd, temp = tempfile.mkstemp(prefix='sulpm_meta_')
    os.close(fd)
    try:
        download(BASE_URL + filename, temp, sudo=False)
        with open(temp, 'r') as f:
            content = f.read()
    finally:
        try:
            os.remove(temp)
        except OSError:
            pass
    return content

def sudo_rm(path):
    # try Python remove first, then fallback to sudo rm -f
    try:
        os.remove(path)
        return True, None
    except FileNotFoundError:
        return False, f'(!) Skipped missing file {path}'
    except PermissionError:
        rc = run(f'sudo rm -f "{path}"')
        if rc == 0:
            return True, None
        else:
            return False, f'(!) Could not delete {path}: Permission denied'
    except Exception as e:
        return False, f'(!) Could not delete {path}: {e}'

# Argument validation
if len(sys.argv) < 2:
    print("Usage: sulpm <package> [owner repo]  OR  sulpm remove <package> ...")
    sys.exit(1)

# --------------------------------------------------
# REMOVE MODE
# --------------------------------------------------
if sys.argv[1].lower() == 'remove':
    if len(sys.argv) < 3:
        print("(!) SULPM: usage: sulpm remove <package>")
        sys.exit(1)

    packages_to_remove = sys.argv[2:]
    if not os.path.exists(log_path):
        print("(!) SULPM: No log file found — nothing to remove.")
        sys.exit(0)

    with open(log_path, 'r') as f:
        lines = f.read().splitlines()

    new_lines = []
    removed_any = False

    i = 0
    while i < len(lines):
        name = lines[i].strip() if i < len(lines) else ''
        if i + 1 >= len(lines):
            # malformed trailing line; keep it
            new_lines.append(lines[i])
            break

        meta_line = lines[i + 1]
        try:
            meta = json.loads(meta_line)
        except json.JSONDecodeError:
            meta = {}

        if name in packages_to_remove:
            print(f'(i) SULPM: Removing {name}')
            for file_key in meta:
                # meta keys should be the installed paths (we record them as such on install)
                path = file_key
                if path.startswith('~'):
                    path = os.path.expanduser(path)
                # attempt deletion
                ok, msg = sudo_rm(path)
                if ok:
                    print(f'(✓) Deleted {path}')
                else:
                    if msg:
                        print(msg)
            removed_any = True
        else:
            new_lines.append(lines[i])
            new_lines.append(lines[i + 1])
        i += 2

    with open(log_path, 'w') as f:
        f.write('\n'.join(new_lines).rstrip() + '\n')

    if removed_any:
        print('(SUCCESS) SULPM: removal complete.')
    else:
        print('(!) SULPM: no matching packages found.')
    sys.exit(0)
# --------------------------------------------------

# Normal install mode
BASE_URL = 'https://raw.githubusercontent.com/Darkwing14/SULPM/main/'
if len(sys.argv) > 3:
    # user provided owner and repo
    BASE_URL = f'https://raw.githubusercontent.com/{sys.argv[2]}/{sys.argv[3]}/main/'

package_name = sys.argv[1]

executable_folder = '/usr/bin/'
print('(i) SULPM: Init.')

print('(i) SULPM: Downloading metadata.')
try:
    JSON = json.loads(fetch_metadata(package_name + '.sulpm'))
except Exception as e:
    print(f'(!) SULPM: could not fetch metadata for {package_name}: {e}')
    sys.exit(1)

Meta = {}

local = input('(Y/N) SULPM: Install locally? (Type yes if you want to avoid using sudo.)\n'
              'Not all programs may support this; if this errors, try saying no.\n> ').lower().startswith('y')  # local means avoid sudo for executables

print('(i) SULPM: Preparing to unpack.')

for file, value in JSON.items():
    # If value is not a non-empty string, treat it as metadata and record it directly
    if not isinstance(value, str) or not value.strip():
        Meta[file] = value
        continue

    src = value
    if not src.startswith('http://') and not src.startswith('https://'):
        src = BASE_URL + src

    handle = 'meta'
    filename = file

    if file.startswith('/'):
        handle = 'root'
        filename = file
    elif file.startswith('~'):
        handle = 'home'
        filename = os.path.expanduser(file)
    elif file.startswith('#'):
        handle = 'executable'
        executable_folder = os.path.expanduser('~/.local/bin/') if local else '/usr/bin/'
        filename = os.path.join(executable_folder, file[1:])
    else:
        # treat as relative path under current directory
        filename = file

    filename = filename.replace('python3.x', pyver)

    dirpath = os.path.dirname(filename)
    if dirpath:
        if handle == 'root':
            # ensure dir exists with sudo
            run(f'sudo mkdir -p "{dirpath}"')
        else:
            os.makedirs(dirpath, exist_ok=True)

    print(f'(i) SULPM: Unpacking {filename}')
    sudo_flag = (handle == 'root' or (handle == 'executable' and not local))
    if handle != 'meta':
        download(src, filename, sudo=sudo_flag)

    if handle == 'executable':
        try:
            if local:
                os.chmod(filename, os.stat(filename).st_mode | 0o111)
            else:
                rc = run(f'sudo chmod +x "{filename}"')
                if rc != 0:
                    print(f'(!) SULPM: could not set executable bit for {filename} using sudo.')
        except Exception as e:
            print(f'(!) SULPM: could not set executable bit for {filename}: {e}')

    # Record installed file path -> source URL so removal later can find it.
    Meta[filename] = src

with open(log_path, 'a') as f:
    f.write(package_name + '\n' + json.dumps(Meta) + '\n')

print('(SUCCESS) SULPM')
