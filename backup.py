#! /usr/bin/env python3

import getopt
import logging
from os import getpid, remove
from os.path import basename, isfile
from random import randrange
from subprocess import call
from sys import argv

NAME = basename(argv.pop(0))
VERSION = '0.8.1'

DEFAULT_OPTIONS = [
    '--verbose',
    '--human-readable',
    '--archive',
    '--hard-links',
    '--acls',
    '--xattrs',
    '--numeric-ids',
    '--noatime',
    '--inplace',
    '--delete',
    '--delete-excluded',
]

LOGGER = logging.getLogger('main')


def print_help():
    print(
        '%s %s, Use rsync to backup and to restore files.\n'
        'Usage: %s [OPTIONS...] CONFIG_FILE [ADDITIONAL_RSYNC_OPTIONS...]\n'
        '\n'
        'OPTIONS:\n'
        '\n'
        '  Informative Output:\n'
        '      -q, --quiet                 keep quiet\n'
        '      -v, --verbose               increase verbosity\n'
        '\n'
        '  Backup Options:\n'
        '          --rsync-opts="..."      replace the default rsync options\n'
        '      -n, --show-cmd              print rsync command and exit\n'
        '\n'
        '  Other Options:\n'
        '      -h, --help                  print this help list\n'
        '      -V, --version               print program version\n'
        '\n\n'
        'Default rsync options: %s\n'
        '\n'
        'Written by Laurence Liu <liuxy6@gmail.com>'
        % (NAME, VERSION, NAME, ' '.join(DEFAULT_OPTIONS)))


def print_version():
    print(
        '%s %s\n'
        'Copyright (C) 2014-2017  Laurence Liu <liuxy6@gmail.com>\n'
        'License GPL v3: GNU GPL version 3 <http://www.gnu.org/licenses/>\n'
        'This program comes with ABSOLUTELY NO WARRANTY.\n'
        'This is free software, and you are welcome to redistribute it.\n'
        '\n'
        'Written by Laurence Liu <liuxy6@gmail.com>'
        % (NAME, VERSION))


def get_conf(filepath, config=None):
    try:
        configlist = open(filepath).read()
        LOGGER.debug('Configuration file: %s', filepath)
    except:
        LOGGER.critical('Cannot read configuration file "%s"', filepath)
        exit()
    try:
        config = config if not config is None else {}
        exec(compile(configlist, '<string>', 'exec'), globals(), config)
        return config
    except:
        LOGGER.critical('Configuration file is incorrect')
        exit()


class BACKUP(object):
    def __init__(self, rsync_opts=None):
        self._ori_dir = ''
        self._des_dir = ''
        self._include = []
        self._include_file = ''
        self._exclude = []
        self._exclude_file = ''
        self._options = ''
        self.add_options(DEFAULT_OPTIONS)
        self.add_options(rsync_opts)

    def set_ori_dir(self, arg):
        self._ori_dir = arg if arg[-1] == '/' else arg + '/'

    def set_des_dir(self, arg):
        self._des_dir = arg

    def set_include(self, arg):
        self._include = arg

    def set_exclude(self, arg):
        self._exclude = arg

    def add_options(self, arg):
        if not isinstance(arg, (tuple, list)):
            LOGGER.debug('arg %s invalid', arg)
            return
        if len(arg) == 0:
            return
        self._options += ' ' + ' '.join(arg)

    def create_inexclude_file(self):
        inexclude = []
        for name in ('include', 'exclude'):
            value = getattr(self, '_%s' % name)
            value = '\n'.join(value) + '\n' if value else ''
            inexclude.append(value)

            if not value:
                continue

            file = open(
                '/tmp/backup.py_%s_%s_%s' % (getpid(), name, randrange(1, 10000)),
                'x',
            )
            file.write(value)
            file.close()
            setattr(self, '_%s_file' % name, file.name)
        return inexclude

    def remove_inexclude_file(self):
        for field in ('_include_file', '_exclude_file'):
            value = getattr(self, field)
            if value and isfile(value):
                remove(value)
                setattr(self, field, '')

    def gen_cmd(self):
        include_from = '--include-from="%s"' % self._include_file if self._include_file else ''
        exclude_from = '--exclude-from="%s"' % self._exclude_file if self._exclude_file else ''
        return 'rsync %s %s %s "%s" "%s"' % (
            self._options,
            include_from,
            exclude_from,
            self._ori_dir,
            self._des_dir)

    def run(self, dry_run=False):
        inexclude = self.create_inexclude_file()
        cmd = self.gen_cmd()
        if dry_run:
            print(cmd)
            print('Include:\n%s\nExclude:\n%s' % tuple(inexclude))
        else:
            LOGGER.debug('Run bash command: %s', cmd)
            if call(cmd, shell=True, executable='/bin/bash'):
                LOGGER.error(
                    'Something went wrong when executing bash command: %s\n',
                    cmd)
        self.remove_inexclude_file()

    ori_dir = property(fset=set_ori_dir)
    des_dir = property(fset=set_des_dir)
    include = property(fset=set_include)
    exclude = property(fset=set_exclude)
    addoptions = property(fset=add_options)


def main():
    show_cmd = False

    try:
        opts, args = getopt.getopt(
            argv,
            'qv nhV',
            ['quiet',
             'verbose',
             'rsync-opts=',
             'show-cmd',
             'help',
             'version',
            ],
        )
    except getopt.GetoptError as error:
        LOGGER.critical(error)
        exit()

    global DEFAULT_OPTIONS
    for o, a in opts:
        if o in ('-q', '--quiet'):
            LOGGER.setLevel(logging.WARN)
            DEFAULT_OPTIONS = DEFAULT_OPTIONS.remove('--verbose')
        elif o in ('-v', '--verbose'):
            LOGGER.setLevel(logging.DEBUG)
        elif o in ('--rsync-opts',):
            DEFAULT_OPTIONS = [a,]
            LOGGER.debug('Set default options: %s', a)
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
        LOGGER.critical('Required argument not found')
        print_help()
        exit()

    for (cl_name, cl) in config_lists.items():
        if cl_name[:6] != 'CONFIG' or not isinstance(cl, dict):
            continue
        LOGGER.debug('Config: %s', cl_name)
        backup = BACKUP(args)
        try:
            if not cl['enabled']:
                LOGGER.debug('Config %s disabled, skipped', cl_name)
                continue

            cl_keys = cl.keys()
            for key, optional in (
                    ('ori_dir', False),
                    ('des_dir', False),
                    ('include', True),
                    ('exclude', True),
                    ('addoptions', True),
                ):
                if not key in cl_keys:
                    if optional:
                        continue
                    else:
                        LOGGER.critical('Cannot found key %s in Config %s', key, cl_name)
                        exit()
                LOGGER.debug('Set %s as %s', key, cl[key])
                setattr(backup, key, cl[key])
        except (IndexError, KeyError, TypeError):
            LOGGER.critical('Configuration file is incorrect')
            exit()

        backup.run(show_cmd)


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)-5.5s] %(asctime)s %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info('Keyboard interrupt received, exit')
        exit()
