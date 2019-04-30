# backup.py

A backup script written in python3.

A simple encapsulation of rsync on linux.

## Requirements

* python3
* bash
* rsync

## Usage

    Usage: backup.py [OPTIONS...] CONFIG_FILE [ADDITIONAL_RSYNC_OPTIONS...]

    OPTIONS:

      Informative Output:
          -q, --quiet                 keep quiet
          -v, --verbose               increase verbosity

      Backup Options:
              --rsync-opts="..."      replace the default rsync options
          -n, --show-cmd              print rsync command and exit

      Other Options:
          -h, --help                  print this help list
          -V, --version               print program version


    Default rsync options: --verbose --human-readable --archive --hard-links --acls --xattrs --numeric-ids --noatime --inplace --delete --delete-excluded

## Configuration

The configuration file of this program is similar to a python module and it must comply with python syntax. You can have some different configuration files and you need to specify one when you run this program.

The configuration file must contain some dictionaries named as 'CONFIG_xxx'. One dictionary represtents one folder you want to backup. Six options can be put into the dictionary:

* enabled    (Required)
* ori_dir    (Required)
* des_dir    (Required)
* include    (Optional)
* exclude    (Optional)
* addoptions (Optional)

## Example

### [Example configuration file](demo.conf)

### Command:

    # backup.py demo.conf

or if you want the quiet:

    # backup.py --quiet demo.conf

## License

Copyright (C) 2014-2019  Laurence Liu <liuxy6@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
