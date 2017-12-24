from pymongo import MongoClient

c = MongoClient('172.31.24.147',27017)
db = c['image_label']
cl = db['quality_golden']

golden = {}
for r in cl.find():
	golden[r['_id']] = r['quality'] 

max_entropy = 8
max_sharpness = 20000
max_colorfulness = 200

def norm(v,min_v=0.0,max_v=1.0):
	return min(max_v,max(min_v,v))

cl = db['quality_score']
for r in cl.find({'_id':{'$in':golden.keys()}}):
	print r['_id'], norm(r['entropy']/max_entropy), norm(r['sharpness']/max_sharpness), norm(r['colorfulness']/max_colorfulness), (1 if golden[r['_id']] == 'high' else 0)
	#print r['_id'], r['entropy'], r['sharpness'], r['colorfulness'], (1 if golden[r['_id']] == 'high' else 0)
	#print r['_id'], norm(r['sharpness']/max_sharpness), norm(r['colorfulness']/max_colorfulness), (1 if golden[r['_id']] == 'high' else 0)

c.close()
