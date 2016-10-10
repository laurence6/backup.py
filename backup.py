#! /usr/bin/env python3
#
# Copyright (C) 2014-2016  Laurence Liu <liuxy6@gmail.com>
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
from os import getpid, remove
from os.path import basename
from random import randrange
from subprocess import call
from sys import argv, exit
from time import time

__NAME__ = basename(argv.pop(0))
__VERSION__ = '0.7.3'

logger = logging.getLogger('main')


def print_help():
    print('%s %s, Use rsync to backup and to restore files.\n'
          'Usage: %s [OPTIONS...] CONFIG_FILE [ADDITIONAL_RSYNC_OPTIONS...]\n'
          '\n'
          'OPTIONS:\n'
          '\n'
          '  Informative Output:\n'
          '      -q, --quiet                 keep quiet\n'
          '      -v, --verbose               increase verbosity\n'
          '\n'
          '  Backup Options:\n'
          '          --rsnyc-opts="..."      replace the default rsync options\n'
          '      -n, --show-cmd              print rsync command and exit\n'
          '\n'
          '  Other Options:\n'
          '      -h, --help                  print this help list\n'
          '      -V, --version               print program version\n'
          '\n\n'
          'Default rsync options: %s\n'
          '\n'
          'Written by Laurence Liu <liuxy6@gmail.com>'\
                  % (__NAME__, __VERSION__, __NAME__, BACKUP.default_options))


def print_version():
    print('%s %s\n'
          'Copyright (C) 2014-2016  Laurence Liu <liuxy6@gmail.com>\n'
          'License GPL v3: GNU GPL version 3 <http://www.gnu.org/licenses/>\n'
          'This program comes with ABSOLUTELY NO WARRANTY.\n'
          'This is free software, and you are welcome to redistribute it.\n'
          '\n'
          'Written by Laurence Liu <liuxy6@gmail.com>' %
          (__NAME__, __VERSION__))


def get_conf(filepath, config=None):
    try:
        configlist = open(filepath).read()
        logger.debug('Configuration file: %s', filepath)
    except IOError:
        logger.critical('Cannot read configuration file "%s"', filepath)
        exit()
    try:
        config = config if not config is None else {}
        exec(compile(configlist, '<string>', 'exec'), globals(), config)
        logger.debug('Config list: %s\n', config)
        return config
    except:
        logger.critical('Configuration file is incorrect')
        exit()


class BACKUP(object):
    default_options = '--verbose --human-readable --archive --hard-links --acls --xattrs --numeric-ids --noatime --inplace --delete --delete-excluded'

    def __init__(self, rsync_opts=''):
        self.__ori_dir = self.__des_dir = self.__include = self.__exclude = self.__options = ''
        self.add_options(rsync_opts)

    def set_ori_dir(self, arg):
        self.__ori_dir = arg if arg[-1] == '/' else arg + '/'

    def set_des_dir(self, arg):
        self.__des_dir = arg

    def set_include(self, arg):
        if len(arg) == 0:
            return
        file = open('/tmp/backup.py_%s_include_%s' %
                    (getpid(), randrange(1000, 9999)), 'w')
        file.write('\n'.join(arg) + '\n')
        file.close()
        self.__include = file.name

    def set_exclude(self, arg):
        if len(arg) == 0:
            return
        file = open('/tmp/pybackup_%s_exclude_%s' %
                    (getpid(), randrange(1000, 9999)), 'w')
        file.write('\n'.join(arg) + '\n')
        file.close()
        self.__exclude = file.name

    def add_options(self, arg):
        if len(arg) == 0:
            return
        self.__options += ' ' + ' '.join(arg)

    def gen_cmd(self):
        include = '--include-from="%s"' % self.__include if self.__include else ''
        exclude = '--exclude-from="%s"' % self.__exclude if self.__exclude else ''
        return 'rsync %s %s %s %s "%s" "%s"' %\
                (self.default_options,\
                        self.__options,\
                        include,\
                        exclude,\
                        self.__ori_dir,\
                        self.__des_dir)

    def run(self):
        start = int(time())
        logger.debug('Run bash command: %s', self.cmd)
        if call(self.cmd, shell=True, executable='/bin/bash'):
            self.logger.error(
                'Something went wrong when executing bash command: %s\n',
                self.cmd)
            return
        self.cleanup()
        finish = int(time())

        totaltime = '%s minutes, %s seconds' %\
                ((finish-start)//60, (finish-start)%60)
        logger.info('Total time: %s\n', totaltime)

    def cleanup(self):
        if self.__include:
            remove(self.__include)
        if self.__exclude:
            remove(self.__exclude)

    ori_dir = property(fset=set_ori_dir)
    des_dir = property(fset=set_des_dir)
    include = property(fset=set_include)
    exclude = property(fset=set_exclude)
    addoptions = property(fset=add_options)
    cmd = property(gen_cmd)


def main():
    show_cmd = False

    try:
        opts, args = getopt.getopt(argv, 'qv nhV',\
                ['quiet', 'verbose', 'rsnyc-opts=', 'show-cmd', 'help', 'version'])
    except getopt.GetoptError as error:
        logger.critical(error)
        exit()
    for o, a in opts:
        if o in ('-q', '--quiet'):
            logger.setLevel(logging.WARN)
            BACKUP.default_options = BACKUP.default_options.replace('--verbose',
                                                                    '')
        elif o in ('-v', '--verbose'):
            logger.setLevel(logging.DEBUG)
        elif o in ('--rsnyc-opts',):
            BACKUP.default_options = a
            logger.debug('Set default options: %s', a)
        elif o in ('-n', '--show-cmd'):
            show_cmd = True
        elif o in ('-h', '--help'):
            print_help()
            exit()
        elif o in ('-V', '--version'):
            print_version()
            exit()

    try:
        config_lists = get_conf(args.pop(0))
    except IndexError:
        logger.critical('Required argument not found')
        print_help()
        exit()

    for (cl_name, cl) in config_lists.items():
        if cl_name[:6] != 'CONFIG' or not isinstance(cl, dict):
            continue
        logger.debug('Arglist: %s', cl_name)
        backup = BACKUP(args)
        try:
            if not cl['enabled']:
                logger.debug('Arglist %s disabled, skipped', cl_name)
                continue
            for key in ('ori_dir', 'des_dir'):
                logger.debug('Set %s as %s', key, cl[key])
                setattr(backup, key, cl[key])
            for key in ('include', 'exclude', 'addoptions'):
                if not key in cl:
                    continue
                logger.debug('Set %s as %s', key, cl[key])
                setattr(backup, key, cl[key])
        except (IndexError, KeyError, TypeError):
            logger.critical('Configuration file is incorrect')
            exit()

        if show_cmd:
            print(backup.cmd)
            backup.cleanup()
        else:
            backup.run()


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)-5.5s] %(asctime)s %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    try:
        main()
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt received, exit')
        exit()
