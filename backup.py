#! /usr/bin/env python3

import logging
from getopt import getopt
from os import getpid, remove
from os.path import basename, isfile
from random import randrange
from subprocess import call
from sys import argv

NAME = basename(argv.pop(0))
VERSION = '0.11.1'

DEFAULT_OPTIONS = [
    '--verbose',
    '--itemize-changes',
    '--human-readable',
    '--archive',
    '--hard-links',
    '--acls',
    '--xattrs',
    '--numeric-ids',
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
        '    -q, --quiet       keep quiet\n'
        '    -v, --verbose     increase verbosity\n'
        '    -n, --show-cmd    print rsync command and exit\n'
        '    -h, --help        print this help list and exit\n'
        '    -V, --version     print program version and exit\n'
        '\n'
        '\n'
        'Default rsync options: %s\n'
        '\n'
        'Written by Laurence Liu <liuxy6@gmail.com>' % (NAME, VERSION, NAME, ' '.join(DEFAULT_OPTIONS))
    )


def print_version():
    print(
        '%s %s\n'
        'Copyright (C) 2014-2020  Laurence Liu <liuxy6@gmail.com>\n'
        'License GPL v3: GNU GPL version 3 <http://www.gnu.org/licenses/>\n'
        'This program comes with ABSOLUTELY NO WARRANTY.\n'
        'This is free software, and you are welcome to redistribute it.\n'
        '\n'
        'Written by Laurence Liu <liuxy6@gmail.com>' % (NAME, VERSION)
    )


class Backupper(dict):
    def create_inexclude_file(self):
        inexclude = []
        for action in ('include', 'exclude'):
            entries = self[action]
            entries = '\n'.join(entries) + '\n' if entries else ''

            inexclude.append(entries)

            if not entries:
                continue

            with open('/tmp/backup.py_%s_%s_%s' % (getpid(), action, randrange(1, 10000)), 'x') as file:
                file.write(entries)

            self['_%s_file' % action] = file.name
        return inexclude

    def remove_inexclude_file(self):
        for field in ('_include_file', '_exclude_file'):
            if field in self:
                filename = self[field]
                if filename and isfile(filename):
                    remove(filename)
                del self[field]

    def gen_cmd(self):
        include_from = '--include-from="%s"' % self['_include_file'] if '_include_file' in self else ''
        exclude_from = '--exclude-from="%s"' % self['_exclude_file'] if '_exclude_file' in self else ''
        return 'rsync %s %s %s "%s" "%s"' % (self['options'], include_from, exclude_from, self['src_dir'], self['dst_dir'])

    def run(self, dry_run):
        if not self['enabled']:
            return

        inexclude = self.create_inexclude_file()

        cmd = self.gen_cmd()

        LOGGER.debug('Run bash command: %s\nInclude:\n%s\nExclude:\n%s', cmd, inexclude[0], inexclude[1])

        if not dry_run:
            if call(cmd, shell=True, executable='/bin/bash'):
                LOGGER.error('Something went wrong when executing bash command: %s\n', cmd)

        self.remove_inexclude_file()


def get_backuppers(args):
    filepath = args.pop(0)
    configfile = open(filepath).read()
    LOGGER.debug('Config file: %s', filepath)

    configs = {}
    exec(compile(configfile, '<string>', 'exec'), {'DEFAULT_OPTIONS': DEFAULT_OPTIONS}, configs)
    configs = {k: get_backupper(v, args) for (k, v) in configs.items() if k.startswith('CONFIG') and isinstance(v, dict)}
    return configs


def get_backupper(config, options_from_cli):
    backupper = Backupper()

    backupper['enabled'] = config['enabled']
    backupper['src_dir'] = config['src_dir']
    backupper['dst_dir'] = config['dst_dir']
    backupper['include'] = config.get('include', None)
    backupper['exclude'] = config.get('exclude', None)

    backupper['options'] = ''

    def append_options(options):
        if isinstance(options, (tuple, list)):
            backupper['options'] += ' ' + ' '.join(options)
        elif isinstance(options, str):
            backupper['options'] += ' ' + options

    if config.get('options_mode', 'append') == 'append':
        append_options(DEFAULT_OPTIONS)
    if 'options' in config:
        append_options(config['options'])
    if options_from_cli:
        append_options(options_from_cli)

    return backupper


def main():
    dry_run = False

    opts, args = getopt(
        argv,
        'qvnhV',
        [
            'quiet',
            'verbose',
            'dry-run',
            'help',
            'version',
        ],
    )

    for o, _ in opts:
        if o in ('-q', '--quiet'):
            LOGGER.setLevel(logging.WARN)
        elif o in ('-v', '--verbose'):
            LOGGER.setLevel(logging.DEBUG)
        elif o in ('-n', '--dry-run'):
            dry_run = True
        elif o in ('-h', '--help'):
            print_help()
            exit()
        elif o in ('-V', '--version'):
            print_version()
            exit()

    if len(args) == 0:
        LOGGER.critical('Required argument not found')
        print_help()
        exit()

    backuppers = get_backuppers(args)
    for (name, backupper) in backuppers.items():
        LOGGER.info('Run %s', name)
        backupper.run(dry_run)


if __name__ == '__main__':
    logging.basicConfig(format='\033[1;34m[%(levelname)s] %(funcName)s: %(message)s\033[0m', datefmt='%H:%M:%S', level=logging.INFO)

    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info('Keyboard interrupt received, exit')
        exit()
