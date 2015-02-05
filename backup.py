#! /usr/bin/env python3
#
# Copyright (C) 2014-2015  Laurence Liu <liuxy6@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import getopt
from os import geteuid
from os.path import basename, dirname
from sys import argv, exit, path
from subprocess import call
from time import localtime, strftime, time


__NAME__ = basename(argv.pop(0))
__VERSION__ = '0.5.0'


def printhelp():
    print('''%s %s, Use rsync to backup and to restore files.
Usage: %s [OPTIONS...] CONFIG_FILE [RSYNC_OPTIONS...]

Informative output:
    -q, --quiet                 keep quiet

Backup Options:
        --backup-opts='...'     change the default rsync options

Other Options:
    -h, --help                  display this help list
    -V, --version               print program version


Default rsync options: %s

Written by Laurence Liu <liuxy6@gmail.com>'''\
        % (__NAME__, __VERSION__, __NAME__, BACKUP.default_options))


def printversion():
    print('''%s %s
Copyright (C) 2014-2015  Laurence Liu <liuxy6@gmail.com>
License GPL v3: GNU GPL version 3 <http://www.gnu.org/licenses/>
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it.

Written by Laurence Liu <liuxy6@gmail.com>''' % (__NAME__, __VERSION__))


def getconf(conffile):
    try:
        conffile = conffile if conffile[-3:] != '.py' else conffile[:-3]

        path.clear()
        path.append('%s' % dirname(conffile))
        conffile = __import__(basename(conffile))

        backup_list = conffile.BACKUP_LIST
    except (ImportError, NameError, ValueError):
        print('Import configuration file error')
        exit()
    except AttributeError:
        print('Configuration file is incorrect')
        exit()
    return backup_list


class BACKUP(object):
    default_options = '--archive --hard-links --acls --xattrs --verbose --delete --delete-excluded'
    __ori_dir = __des_dir = __include = __exclude = __options = totaltime = ''

    def __init__(self, rsync_opts):
        self.set_options(rsync_opts)

    def set_ori_dir(self, arg):
        self.__ori_dir = arg if arg[-1] == '/' else arg+'/'

    def set_des_dir(self, arg):
        self.__des_dir = arg

    def set_include(self, arg):
        self.__include = ' '.join(['--include="%s"' % x for x in arg])

    def set_exclude(self, arg):
        self.__exclude = ' '.join(['--exclude="%s"' % x for x in arg])

    def set_options(self, arg):
        self.__options += ' '.join(arg)

    def run(self):
        cmd = 'rsync %s %s %s %s "%s" "%s"' %\
                (self.default_options, self.__options, self.__include, self.__exclude, self.__ori_dir, self.__des_dir)

        start = int(time())
        if call(cmd, shell=True, executable='/bin/bash'):
            print('Something went wrong... The bash command:'+'\n'+cmd+'\n')
            return
        finish = int(time())

        self.totaltime = 'total time: %s minutes, %s seconds' %\
                ((finish-start)//60, (finish-start)%60)
        print(self.totaltime+'\n')

    def log(self):
        try:
            with open('%s/%s' % (self.__des_dir, strftime('%Y-%m-%d %H:%M:%S', localtime())), 'w')\
                    as logfile:
                logfile.write(self.totaltime)
        except (FileNotFoundError, PermissionError):
            pass

    ori_dir = property(fset=set_ori_dir)
    des_dir = property(fset=set_des_dir)
    include = property(fset=set_include)
    exclude = property(fset=set_exclude)
    options = property(fset=set_options)


def main():
    try:
        opts, args = getopt.getopt(argv, 'q hV', ['quiet', 'backup-opts=', 'help', 'version'])
    except getopt.GetoptError as error:
        print(error)
        exit()
    for o, a in opts:
        if o in ('-q', '--quiet'):
            BACKUP.default_options = BACKUP.default_options.replace('--verbose', '')
        elif o in ('--backup-opts',):
            BACKUP.default_options = a
        elif o in ('-h', '--help'):
            printhelp()
            exit()
        elif o in ('-V', '--version'):
            printversion()
            exit()

    if geteuid() != 0:
        print('Non root user')
        exit()

    try:
        backup_list = getconf(args.pop(0))
    except IndexError:
        print('Required argument not found')
        exit()

    for arglist in backup_list:
        backup = BACKUP(args)
        try:
            if not arglist['enabled']:
                continue
            for key in ('ori_dir', 'des_dir', 'include', 'exclude', 'options'):
                setattr(backup, key, arglist[key])
        except KeyError as error:
            print('%s in configuration file is incorrect' % error)
            exit()
        except IndexError:
            print('Configuration file is incorrect')
            exit()

        try:
            backup.run()
            backup.log()
        except KeyboardInterrupt:
            exit()


if __name__ == '__main__':
    main()
