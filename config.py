DES = '/mnt/Backup/'
BACKUP_LIST = [
               {
                   'enabled': True,
                   'ori_dir': '/',
                   'des_dir': 'root',
                   'include': [],
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
                   ],
                   'options': [],
               },
               {
                   'enabled': True,
                   'ori_dir': '/home/',
                   'des_dir': 'home',
                   'include': [],
                   'exclude': [
                       'lost+found',
                       '*cache*',
                       '*Cache*',
                       '*.log*',
                       '*.old',
                       '*tmp*',
                   ],
                   'options': [],
               },
           ]
