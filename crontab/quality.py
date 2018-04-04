import sys
import requests
import json
import time
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool


def when():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: python quality.py last_ts.txt'
        sys.exit()

    last_ts = int(time.time() - 72 * 3600)
    with open(sys.argv[1]) as fin:
        last_ts = int(fin.read())

    c1 = MongoClient('mongodb://172.31.23.34:27017,172.24.22.248:27017/?replicaset=rs-userprofile')
    c2 = MongoClient('mongodb://172.31.20.160:27017,172.31.20.161:27017,172.31.20.162:27017/?replicaSet=rs2')

    cr1 = c1['documentLabels']['poi']
    cr2 = c2['serving']['displayDocument']

    with cr1.find({'lastUpdate': {'$gte': last_ts}}).limit(20000) as result:
        docs = [d for d in result]

    def process(d):
        if 'quality' not in d:
            try:
                one = cr2.find_one({'_id': d['_id']}, {'image': 1})
                if not one:
                    sys.stderr.write('(%s) ERROR: docid not exists: %s\n' % (when(), d['_id']))
                    q = 'high'
                elif not one.get('image', False):
                    sys.stderr.write('(%s) ERROR: image not exists: %s\n' % (when(), d['_id']))
                    q = 'high'
                else:
                    imgid = one['image']
                    r = requests.get('http://a4api.ha.nb.com/Website/image/quality-check?image=%s' % imgid)
                    j = json.loads(r.content)
                    q = j['result'][imgid]['quality']
                cr1.update({'_id': d['_id']}, {'$set': {'quality': q}})
            except Exception, e:
                t, o, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                sys.stderr.write('(%s) ERROR: Exception in %s, Line %s: %s, docid %s\n' % (when(), filename, str(lineno), e, d['_id']))
        return d['lastUpdate']

    pool = ThreadPool(20)
    results = pool.map(process, docs)
    pool.close()
    pool.join()

    c1.close()
    c2.close()

    if len(results) > 0:
        with open(sys.argv[1], 'w') as fout:
            fout.write(str(max(results)))

    print when(), 'INFO:', len(results), 'processed'
