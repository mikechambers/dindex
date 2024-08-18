# dindex

dindex is a simple python3 script that generates directory index files for web servers. It is meant to be used for individual directories, and makes it easy to style and customize the HTML and CSS.

Directories and files are listed separately, and are ordered in reverse chronological order based on when the entries were last updated.

## Installation

The script requires Python3 and a number of libraries to be installed. You can install the required libraries with:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, simply call it, passing in the directory that you want to create an index file for:

```bash
python3 dindex.py --input-dir /var/www/files/
```

This will create an **index.html** and **style.css** file in the specified folder, which displays and links the contents of that folder.

You can find a complete list of options by running:

```bash
python3 dindex.py --help
```

## Known Issues

* Only displays files and directories, and not other entries such as symlinks
* Displayed date is based on locale and timezone where generated

## Questions, Feature Requests, Feedback

If you have any questions, feature requests, need help, or just want to chat, you can ping me on [Twitter](https://twitter.com/mesh) or via email at [mikechambers@gmail.com](mailto:mikechambers@gmail.com).

You can also log bugs and feature requests on the [issues page](https://github.com/mikechambers/dindex/issues).

## License

Project released under a [MIT License](LICENSE.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE.md)