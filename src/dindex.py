import argparse
import sys
import os
import datetime
from jinja2 import Environment, FileSystemLoader
import platform
import shutil
import ctypes
from zoneinfo import ZoneInfo

VERSION = "0.85.1"
INDEX_TEMPLATE = "index.html"
STYLE_FILE = "style.css"

verbose = False
input_dir = None
env = None

show_hidden = False
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


def build_index(items : dict, input_dir : str):

    template = env.get_template(INDEX_TEMPLATE)

    generated_date = add_timezone(datetime.datetime.now())

    context = {
        "items":items,
        "version":VERSION,
        "title":"Index",
        "generated_date": generated_date
    }

    output = template.render(context)

    file_path = os.path.join(input_dir, "index.html")

    if verbose:
        print(f"Writing file to : {file_path}")

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(output)

def parse_input_dir(input_dir : str) -> dict:

    paths = []
    for f in os.listdir(input_dir):

        if f in ignore_list:
            continue

        if not show_hidden and is_hidden(f):
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

        path = item["path"]
        
        if os.path.isdir(path):
            data["dirs"].append(item)
        elif os.path.isfile(path):

            item["size"] = get_file_size_in_kb(path)
            data["files"].append(item)
        else:
            continue

    return data

def get_file_size_in_kb(path : str) -> int:
    if not os.path.isfile(path):
        raise ValueError(f"The path {path} is not a valid file.")

    # Get the file size in bytes
    file_size_in_bytes = os.path.getsize(path)
    
    # Convert bytes to kilobytes
    file_size_in_kb = int(file_size_in_bytes / 1024)
    
    return file_size_in_kb

def is_hidden(path : str) -> bool:
    if platform.system() == 'Windows':
        # Check for hidden attribute on Windows
        attribute = ctypes.windll.kernel32.GetFileAttributesW(path)
        return attribute & 2  # FILE_ATTRIBUTE_HIDDEN is 2
    else:
        # Check for leading dot on Unix-like systems (Linux, macOS)
        return os.path.basename(path).startswith('.')

def get_creation_date(path : str) -> datetime:

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


    # Convert the creation time to a readable format
    creation_date = datetime.datetime.fromtimestamp(creation_time)
    localized_creation_date = add_timezone(creation_date)

    return localized_creation_date

def add_timezone(date : datetime.datetime) -> datetime.datetime:
    system_timezone = datetime.datetime.now().astimezone().tzinfo
    localized_creation_date = date.replace(tzinfo=system_timezone)

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
        '--show-hidden',
        dest='show_hidden', 
        action='store_true', 
        help='Whether hidden files should be displayed.'
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        dest="input_dir",
        help='The input_director to create the index file for'
    )

    parser.add_argument(
        '--ignore-list', 
        nargs='*',  # This means one or more arguments
        dest="ignore_list",
        type=str,   # Ensure that the inputs are treated as strings
        help='List of files to ignore. Use with no arguments to override default list.'
    )

    args = parser.parse_args()

    if not args.version and not args.input_dir:
        parser.error('--input-dir or --version is requries')

    if args.version:
        print(f"Digest version : {VERSION}")
        print("https://github.com/mikechambers/dispatch")
        sys.exit()

    if args.ignore_list is not None:
        ignore_list = args.ignore_list



    verbose = args.verbose
    input_dir = args.input_dir
    show_hidden = args.show_hidden

    try:
        main()
    except Exception as e:
        print(f"An error occurred. Aborting : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)