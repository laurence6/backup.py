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
import logging
from os.path import basename
from subprocess import call
from sys import argv, exit
from time import time


__NAME__ = basename(argv.pop(0))
__VERSION__ = '0.5.6'

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger()


def printhelp():
    print('%s %s, Use rsync to backup and to restore files.\n'
          'Usage: %s [OPTIONS...] CONFIG_FILE [RSYNC_OPTIONS...]\n'
          '\n'
          'Informative output:\n'
          '    -q, --quiet                 keep quiet\n'
          '    -v, --verbose               increase verbosity\n'
          '\n'
          'Backup Options:\n'
          '        --backup-opts="..."     change the default rsync options\n'
          '    -n, --show-cmd              print rsync command and exit\n'
          '\n'
          'Other Options:\n'
          '    -h, --help                  print this help list\n'
          '    -V, --version               print program version\n'
          '\n'
          '\n'
          'Default rsync options: %s\n'
          '\n'
          'Written by Laurence Liu <liuxy6@gmail.com>'\
                  % (__NAME__, __VERSION__, __NAME__, BACKUP.default_options))


def printversion():
    print('%s %s\n'
          'Copyright (C) 2014-2015  Laurence Liu <liuxy6@gmail.com>\n'
          'License GPL v3: GNU GPL version 3 <http://www.gnu.org/licenses/>\n'
          'This program comes with ABSOLUTELY NO WARRANTY.\n'
          'This is free software, and you are welcome to redistribute it.\n'
          '\n'
          'Written by Laurence Liu <liuxy6@gmail.com>' % (__NAME__, __VERSION__))


def getconf(filepath, module=type(getopt)):
    try:
        conf = open(filepath).read()
        logger.debug('Configuration file: %s' % filepath)
    except IOError:
        logger.critical('Cannot read configuration file "%s"' % filepath)
        exit()
    m = module(basename(filepath))
    try:
        exec(compile(conf, '<string>', 'exec'), m.__dict__)
        logger.debug('Config list: %s' % m.CONFIG_LIST)
        return m.CONFIG_LIST
    except (AttributeError, NameError, SyntaxError):
        logger.critical('Configuration file is incorrect')
        exit()


class BACKUP(object):
    default_options = '--verbose --archive --hard-links --acls --xattrs --delete --delete-excluded'
    __ori_dir = __des_dir = __include = __exclude = __options = ''

    def __init__(self, rsync_opts=''):
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

    def get_cmd(self):
        return 'rsync %s %s %s %s "%s" "%s"' %\
                (self.default_options,\
                        self.__options,\
                        self.__include,\
                        self.__exclude,\
                        self.__ori_dir,\
                        self.__des_dir)

    def run(self):
        start = int(time())
        logger.debug('Bash command: %s' % self.cmd)
        if call(self.cmd, shell=True, executable='/bin/bash'):
            logger.error('Something went wrong when executing bash command: %s\n' % self.cmd)
            return
        finish = int(time())

        totaltime = '%s minutes, %s seconds' %\
                ((finish-start)//60, (finish-start)%60)
        logger.info('Total time: %s\n' % totaltime)

    ori_dir = property(fset=set_ori_dir)
    des_dir = property(fset=set_des_dir)
    include = property(fset=set_include)
    exclude = property(fset=set_exclude)
    options = property(fset=set_options)
    cmd = property(get_cmd)


def main():
    show_cmd = False

    try:
        opts, args = getopt.getopt(argv, 'qv nhV',\
                ['quiet', 'verbose', 'backup-opts=', 'show-command', 'help', 'version'])
    except getopt.GetoptError as error:
        logger.critical(error)
        exit()
    for o, a in opts:
        if o in ('-q', '--quiet'):
            logger.setLevel(logger.level+10)
            BACKUP.default_options = BACKUP.default_options.replace('--verbose', '')
        elif o in ('-v', '--verbose'):
            logger.setLevel(logger.level-10)
            BACKUP.default_options = BACKUP.default_options + ' --verbose'
        elif o in ('-n', '--show-cmd'):
            show_cmd = True
        elif o in ('--backup-opts',):
            BACKUP.default_options = a
            logger.debug('Set default options: %s' % a)
        elif o in ('-h', '--help'):
            printhelp()
            exit()
        elif o in ('-V', '--version'):
            printversion()
            exit()

    try:
        config_list = getconf(args.pop(0))
    except IndexError:
        logger.critical('Required argument not found')
        printhelp()
        exit()

    for arglist in config_list:
        logger.debug('Arglist: %s' % arglist)
        backup = BACKUP(args)
        try:
            if not arglist['enabled']:
                logger.debug('Arglist %s disabled, skipped' % arglist)
                continue
            for key in ('ori_dir', 'des_dir', 'include', 'exclude', 'options'):
                logger.debug('Set %s as %s' % (key, arglist[key]))
                setattr(backup, key, arglist[key])
        except (IndexError, KeyError, TypeError):
            logger.critical('Configuration file is incorrect')
            exit()

        if show_cmd:
            print(backup.cmd)
        else:
            backup.run()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Receive the keyboard interrupt, exit')
        exit()
