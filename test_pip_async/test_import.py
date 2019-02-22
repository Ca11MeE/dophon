from test_pip_async import d_import


d_import('dophon_db')
d_import('dophon_mq')

import dophon_db
import dophon_mq

print(dophon_db)
print(dophon_mq)

while True:
    pass