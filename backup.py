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

from subprocess import call
from time import localtime, strftime, time
from os import geteuid
from os.path import basename, dirname
from sys import argv, path


__version__ = '0.2.0'

class BACKUP:
    def __init__(self):
        self.ori_dir = self.des_dir = self.include = self.exclude = self.options = self.command = self.totaltime = ''

    def set_ori_dir(self, arg):
        self.ori_dir = arg if arg[-1] == '/' else arg+'/'

    def set_des_dir(self, arg):
        self.des_dir = DES+arg

    def set_include(self, arg):
        self.include = ' '.join(['--include="%s"' % x for x in arg])

    def set_exclude(self, arg):
        self.exclude = ' '.join(['--exclude="%s"' % x for x in arg])

    def set_options(self, arg):
        arg.extend(argv)
        self.options = ' '.join(arg)

    def run(self):
        self.command = 'rsync -aHAXv --delete --delete-excluded %s %s %s "%s" "%s"' %\
                (self.options, self.include, self.exclude, self.ori_dir, self.des_dir)

        start = int(time())
        if call(self.command, shell=True, executable='/bin/bash'):
            print('Something went wrong... The bash command:'+'\n'+self.command+'\n')
            return
        finish = int(time())

        self.totaltime = 'total time: %s minutes, %s seconds' %\
                ((finish-start)//60, (finish-start)%60)
        print(self.totaltime+'\n')
        self.log()

    def log(self):
        try:
            logfile = open('%s/%s' % (self.des_dir,\
                    strftime('%Y-%m-%d %H:%M:%S', localtime())), 'w')
            logfile.write(self.totaltime)
            logfile.close()
        except FileNotFoundError:
            pass

    bk_ori_dir = property(fset=set_ori_dir)
    bk_des_dir = property(fset=set_des_dir)
    bk_include = property(fset=set_include)
    bk_exclude = property(fset=set_exclude)
    bk_options = property(fset=set_options)


if __name__ == '__main__':
    del argv[0]
    try:
        CONFFILE = argv.pop(0) if argv[0][-3:] != '.py' else argv.pop(0)[:-3]

        path.append(dirname(CONFFILE))
        CONF = __import__(basename(CONFFILE))

        DES = CONF.DES
        BACKUP_LIST = CONF.BACKUP_LIST
    except IndexError:
        print('Required argument not found')
        exit()
    except ImportError:
        print('Import configuration file error')
        exit()
    except AttributeError:
        print('Configuration file is incorrect')
        exit()

    if geteuid() != 0:
        print('Non root user')
        exit()

    for arglist in BACKUP_LIST:
        backup = BACKUP()
        try:
            if arglist['enabled']:
                for key in ('ori_dir', 'des_dir', 'include', 'exclude', 'options'):
                    setattr(backup, 'bk_'+key, arglist[key])
        except KeyError as e:
            print('%s in config file is incorrect' % e)
            exit()
        backup.run()
