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


__version__ = '0.1.0'

if __name__ == '__main__':
    try:
        conffile = argv[1] if argv[1][-3:] != '.py' else argv[1][:-3]

        path.append(dirname(conffile))
        conf = __import__(basename(conffile))

        DES = getattr(conf, 'DES')
        BACKUP_LIST = getattr(conf, 'BACKUP_LIST')
    except AttributeError:
        print('Config file contains some error')
        exit()
    except ImportError:
        print('Import config file error')
        exit()
    except IndexError:
        print('Required argument not found')
        exit()

    if geteuid() != 0:
        print('Non root user')
        exit()

    for arglist in BACKUP_LIST:
        if arglist['enabled']:
            ori_dir, des_dir, include, exclude, options = arglist['ori_dir'], arglist['des_dir'], arglist['include'], arglist['exclude'], arglist['options']
            ori_dir = ori_dir if ori_dir[-1] == '/' else ori_dir+'/'
            des_dir = DES+des_dir
            include = ' '.join(['--include="%s"' % x for x in include])
            exclude = ' '.join(['--exclude="%s"' % x for x in exclude])
            options = ' '.join(options)
            command = 'rsync -aHAXv --delete --delete-excluded %s %s %s "%s" "%s"' % (options, include, exclude, ori_dir, des_dir)

            start = int(time())
            if call(command, shell=True, executable='/bin/bash'):
                print('Something went wrong... The bash command:'+'\n'+command+'\n')
                continue
            finish = int(time())

            totaltime = 'total time: %s minutes, %s seconds' % ((finish-start)//60, (finish-start)%60)
            print(totaltime+'\n')
            try:
                logfile = open('%s/%s' % (des_dir, strftime('%Y-%m-%d %H:%M:%S', localtime())), 'w')
                logfile.write(totaltime)
                logfile.close()
            except FileNotFoundError:
                pass
