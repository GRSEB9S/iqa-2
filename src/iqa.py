#!/usr/bin/python
# coding=utf-8

'''
iqa.py

Class for image quality assessment.

Created by Xu Kaifeng on 2017.12.20
Particle Holding Inc. All rights reserved.
'''

import sys,cv2,urllib
import numpy as np

class IQA:
	def __init__(self, imgid):
		url = 'http://img.particlenews.com/image.php?type=_400x400&url='+imgid
		resp = urllib.urlopen(url)
		image = image = np.asarray(bytearray(resp.read()), dtype="uint8")
		self.img = cv2.imdecode(image, cv2.IMREAD_COLOR)
		self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

	def sharpness(self):
		# https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
		return cv2.Laplacian(self.gray, cv2.CV_64F).var()

	def colorfulness(self):
		# https://www.pyimagesearch.com/2017/06/05/computing-image-colorfulness-with-opencv-and-python/
		B,G,R = cv2.split(self.img.astype("float"))
		rg = np.absolute(R - G)
		yb = np.absolute(0.5 * (R + G) - B)
		rbMean, rbStd = np.mean(rg), np.std(rg)
		ybMean, ybStd = np.mean(yb), np.std(yb)
		stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
		meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
		return stdRoot + (0.3 * meanRoot)
		
	def entropy(self):
		# https://cn.mathworks.com/help/images/ref/entropy.html
		hist = cv2.calcHist([self.gray],[0],None,[256],[0,256])
		hist = hist.ravel()/hist.sum()
		logs = np.log2(hist+0.000001)
		return -1 * (hist*logs).sum()


if __name__ == '__main__':
	for line in sys.stdin:
		imgid = line.strip()
		iqa = IQA(imgid)
		print 'sharpness:',iqa.sharpness()
		print 'colorfulness:',iqa.colorfulness()
		print 'entropy',iqa.entropy()
