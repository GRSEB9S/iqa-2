import sys

for line in sys.stdin:
	print 'curl http://internal-a4api-74034796.us-west-2.elb.amazonaws.com/Website/video/image-quality-check?image='+line.strip()

