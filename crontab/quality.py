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

    with MongoClient('172.31.23.34:27017,172.24.22.248:27017', replicaset='rs-userprofile') as c:
        last_ts = int(time.time() - 72 * 3600)
        with open(sys.argv[1]) as fin:
            last_ts = int(fin.read())

        cl = c['documentLabels']['poi']
        docs = [d for d in cl.find({'lastUpdate': {'$gte': last_ts}}).limit(20000)]

        def process(d):
            docid = d['_id']
            if 'quality' not in d:
                try:
                    r = requests.get('http://a4api.ha.nb.com/Website/contents/content?docid=%s&fields=image' % docid)
                    j = json.loads(r.content)
                    if 'documents' not in j:
                        raise Exception('docid not exists')
                    if 'image' not in j['documents'][0]:
                        raise Exception('image not exists')
                    imgid = j['documents'][0]['image']
                    r = requests.get('http://a4api.ha.nb.com/Website/image/quality-check?image=%s' % imgid)
                    j = json.loads(r.content)
                    q = j['result'][imgid]['quality']
                    cl.update({'_id':docid},{'$set':{'quality':q}})
                except Exception, e:
                    t, o, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    sys.stderr.write('(%s) ERROR: Exception in %s, Line %s: %s, docid %s\n' % (when(), filename, str(lineno), e, docid))
            return d['lastUpdate']

        pool = ThreadPool(20)
        results = pool.map(process, docs)
        pool.close()
        pool.join()

        if len(results) > 0:
            with open(sys.argv[1], 'w') as fout:
                fout.write(str(max(results)))

        print when(), 'INFO:', len(results), 'processed'
