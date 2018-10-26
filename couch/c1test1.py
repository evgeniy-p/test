from couchbase.bucket import Bucket
from couchbase import exceptions
from random import choice
import sys

login = 'test_user'
password = 'test_user'
host ='192.168.10.94'
port = 8091
cb_name = 'test_bucket'
bucket_type = 'couchbase'

ringme_cb = Bucket('couchbase://{host}:{port}/{cb_name}'.format(host=host, port=port, cb_name=cb_name), username=login,
                   password=password)


for row in ringme_cb.n1ql_query('SELECT meta().id FROM test_bucket;'):
    for ans in ringme_cb.n1ql_query('SELECT * FROM test_bucket WHERE meta().id="{where}"'.format(where=row['id'])):
        pass
'''
for i in range(100000):
    try:
        ringme_cb.insert(sys.argv[0] + str(i+1000002))
    except exceptions.KeyExistsError:
        print('exist, pass')
'''

print('ok')



