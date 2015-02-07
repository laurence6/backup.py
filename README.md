pybackup
========

A backup script written in python3.

A simple encapsulation of rsync on linux.


## Usage

<pre>
backup.py [OPTIONS...] CONFIG_FILE [RSYNC_OPTIONS...]

Informative output:
    -q, --quiet                 keep quiet

Backup Options:
        --backup-opts='...'     change the default rsync options

Other Options:
    -h, --help                  display this help list
    -V, --version               print program version


Default rsync options: --archive --hard-links --acls --xattrs --verbose --delete --delete-excluded
</pre>


## License

Copyright (C) 2014-2015  Laurence Liu <liuxy6@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
