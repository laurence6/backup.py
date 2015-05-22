# pybackup 0.6.0

A backup script written in python3.

A simple encapsulation of rsync on linux.


# Usage

    Usage: backup.py [OPTIONS...] CONFIG_FILE [ADDITIONAL_RSYNC_OPTIONS...]

    OPTIONS:

      Informative Output:
          -q, --quiet                 keep quiet
          -v, --verbose               increase verbosity

      Backup Options:
              --rsnyc-opts="..."      replace the default rsync options
          -n, --show-cmd              print rsync command and exit

      Other Options:
          -h, --help                  print this help list
          -V, --version               print program version


    Default rsync options: --verbose --archive --hard-links --acls --xattrs --delete --delete-excluded


# Configuration

The configuration file of this program is similar to a python module and it must comply with python syntax. You can have some different configuration files and you need to specify one when you run this program.

The configuration file must contain a list named 'CONFIG_LIST' and you can put some items which represtent folders you want to backup into it. Each item must be a dictionary which include five items: 'enabled', 'ori_dir', 'des_dir', 'include', 'exclude', 'options'.


# Example

### Configuration file:

/root/demo.conf

```python
CONFIG_ROOT = {
                  'enabled': True,               # Required. Set False if you don't want to backup this folder
                  'ori_dir': '/',                # Required. Original directory
                  'des_dir': '/mnt/Backup/root', # Required. Destination directory
                  'include': [
                      '/home/user/',
                  ],                             # Optional. Do NOT exclude these files
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
                  ],                             # Optional. Exclude these files
                  'addoptions': [
                      '--log-file=/mnt/root-log',
                  ],                             # Optional. Some additional options for rsync
              }
CONFIG_HOME = {
                  'enabled': True,
                  'ori_dir': '/home/',
                  'des_dir': '/mnt/Backup/home',
                  'include': [],
                  'exclude': [
                      'lost+found',
                      '*cache*',
                      '*Cache*',
                      '*.log*',
                      '*.old',
                      '*tmp*',
                  ],
                  'addoptions': [
                      '--log-file=/mnt/home-log',
                  ],
              }
```

### Command:

    # backup.py /root/demo.conf

or if you want the quiet:

    # backup.py --quiet /root/demo.conf


# License

Copyright (C) 2014-2015  Laurence Liu <liuxy6@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
