import argparse
import sys
import os
import datetime
from jinja2 import Environment, FileSystemLoader
import platform
import shutil
import ctypes

VERSION = "0.85.1"
INDEX_TEMPLATE = "index.html"
STYLE_FILE = "style.css"

verbose = False
input_dir = None
env = None

ignore_hidden = True
ignore_list = ["index.html", "style.css"]

def main():
    global env, input_dir

    input_dir = os.path.abspath(input_dir)
    if not os.path.exists(input_dir):
        print(f"input_dir does not exists : {input_dir}" )
        sys.exit(1)

    env = Environment(loader=FileSystemLoader('templates'))

    items = parse_input_dir(input_dir)

    build_index(items, input_dir)

    if verbose:
        print(f"Copying CSS file")
    shutil.copy2(
        os.path.abspath(STYLE_FILE),
        os.path.join(input_dir, STYLE_FILE)
    )


def build_index(items, input_dir):

    template = env.get_template(INDEX_TEMPLATE)

    context = {
        "items":items,
        "version":VERSION,
        "title":"title"
    }

    output = template.render(context)

    file_path = os.path.join(input_dir, "index.html")

    if verbose:
        print(f"Writing file to : {file_path}")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(output)

def parse_input_dir(input_dir):

    paths = []
    for f in os.listdir(input_dir):

        if f in ignore_list:
            continue

        if ignore_hidden and is_hidden(f):
            continue

        path = os.path.join(input_dir, f)
        date = get_creation_date(path)

        paths.append({
            "name":f,
            "path":path,
            "date":date,
            "size":None
        })

    paths.sort(key=lambda x: x['date'], reverse=True)

    data = {"files":[], "dirs":[]}

    for item in paths:

        if os.path.isdir(item["path"]):
            data["dirs"].append(item)
        elif os.path.isfile(item["path"]):

            item["size"] = get_file_size_in_kb(item["path"])
            data["files"].append(item)
        else:
            continue

    return data

def get_file_size_in_kb(file_path):
    """
    Returns the size of the file at the given path in kilobytes (KB).
    
    :param file_path: Path to the file
    :return: Size of the file in KB
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"The path {file_path} is not a valid file.")

    # Get the file size in bytes
    file_size_in_bytes = os.path.getsize(file_path)
    
    # Convert bytes to kilobytes
    file_size_in_kb = int(file_size_in_bytes / 1024)
    
    return file_size_in_kb

def is_hidden(filepath):
    if platform.system() == 'Windows':
        # Check for hidden attribute on Windows
        attribute = ctypes.windll.kernel32.GetFileAttributesW(filepath)
        return attribute & 2  # FILE_ATTRIBUTE_HIDDEN is 2
    else:
        # Check for leading dot on Unix-like systems (Linux, macOS)
        return os.path.basename(filepath).startswith('.')

def get_creation_date(path):

    # Check the operating system
    if platform.system() == 'Windows':
        # On Windows, use the creation time
        creation_time = os.path.getctime(path)
    else:
        # On Unix-like systems, try to use the birth time (available on some systems)
        stat = os.stat(path)
        try:
            creation_time = stat.st_birthtime
        except AttributeError:
            # If birth time is not available, fallback to the last metadata change time
            creation_time = stat.st_mtime

    from zoneinfo import ZoneInfo
    # Convert the creation time to a readable format
    creation_date = datetime.datetime.fromtimestamp(creation_time)
    system_timezone = datetime.datetime.now().astimezone().tzinfo
    localized_creation_date = creation_date.replace(tzinfo=system_timezone)

    return localized_creation_date

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Creates an index.html file for a input_directory."
    )

    parser.add_argument(
        '--version',
        dest='version', 
        action='store_true', 
        help='display current version'
    )

    parser.add_argument(
        '--verbose',
        dest='verbose', 
        action='store_true', 
        help='display additional information as script runs'
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        dest="input_dir",
        help='The input_director to create the index file for'
    )

    args = parser.parse_args()

    if not args.version and not args.input_dir:
        parser.error('--input-dir is required unless --version is specified')

    if args.version:
        print(f"Digest version : {VERSION}")
        print("https://github.com/mikechambers/dispatch")
        sys.exit()

    verbose = args.verbose
    input_dir = args.input_dir

    try:
        main()
    except Exception as e:
        print(f"An error occurred. Aborting : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)