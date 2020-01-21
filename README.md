# backup.py

A backup script written in Python3.

A simple encapsulation of Rsync.

## Requirements

* Python3
* Rsync
* Bash

## Usage

    Usage: backup.py [OPTIONS...] CONFIG_FILE [ADDITIONAL_RSYNC_OPTIONS...]

    OPTIONS:

        -q, --quiet       keep quiet
        -v, --verbose     increase verbosity
        -n, --show-cmd    print rsync command and exit
        -h, --help        print this help list and exit
        -V, --version     print program version and exit

    Default rsync options: --verbose --human-readable --archive --hard-links --acls --xattrs --numeric-ids --inplace --delete --delete-excluded


## Configuration

* enabled      (Required)
* src_dir      (Required)
* dst_dir      (Required)
* include      (Optional)
* exclude      (Optional)
* options      (Optional)
* options_mode (Optional)

## Example

### Example configuration file

```python
CONFIG_ROOT = {
    'enabled': True,               # Required. Set True to enable this config block.
    'src_dir': '/',                # Required. Source directory.
    'dst_dir': '/mnt/Backup/root', # Required. Destination directory.
    'include': [
        '/home/user/',
    ],                             # Optional. Include these files.
    'exclude': [
        'lost+found',
        '/dev/*',
        '/proc/*',
        '/sys/*',
        '/tmp/*',
        '/run/*',
        '/mnt/*',
        '/media/*',
        '/var/tmp/*',
        '/home/*',
    ],                             # Optional. Exclude these files.
    'options_mode': '',            # Optional. 'append' (default): append options to the default rsync options, 'override': set rsync options to options.
    'options': [
        '--log-file=/mnt/root-log',
    ],                             # Optional. Rsync options.
}
CONFIG_HOME = {
    'enabled': True,
    'src_dir': '/home/',
    'dst_dir': '/mnt/Backup/home',
}
```

### Command:

    $ backup.py config.py

## License

Copyright (C) 2014-2020  Laurence Liu <liuxy6@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
