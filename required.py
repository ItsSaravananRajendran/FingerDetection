import cv2                              
import numpy as np
import math   
from shapely.geometry import LineString
from shapely.geometry import Point
import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)



def nothing(x):
    pass

def distAB(x,y):  
	x = np.array(x)
	y = np.array(y) 
	return np.sqrt(np.sum((x-y)**2))

def maxCont(contours):
	max_area = 0
	for i in range(len(contours)):
		cnt=contours[i]
		area = cv2.contourArea(cnt)
		if(area>max_area):
			max_area=area
			ci=i
	return contours[ci]

def pairFingerTipAndCenter(fingerTip, centerList , contourList):
	paired = []
	counter = 0
	for I in centerList:
		maxDist = 0
		maxCoOr = None
		for J in fingerTip:
			if (cv2.pointPolygonTest(contourList[counter],J,False) == 0):
				distIJ = distAB(I,J)
				if(distIJ >= maxDist):
					maxDist = distIJ
					maxCoOr = [J , I]
		paired.append(maxCoOr)
		counter = counter + 1
	return paired

def contourCenter(cont):
	for I in cont:
		if not(cv2.contourArea(I) == 0):
			momCont = cv2.moments(I)
			cx = int(momCont['m10']/momCont['m00'])
			cy = int(momCont['m01']/momCont['m00'])
			return (cx,cy)

def pairAll(pairedPoints, x):
	counter = 0
	for i in pairedPoints:
		(x1,y1) = pairedPoints[counter][0]
		(x2,y2) = pairedPoints[counter][1]
		m = (y2-y1)/((1.0)*(x2-x1))
		c = y1 - (m*x1)
		y = m*x + c
		end = (x,y)
		pairedPoints[counter].append(end)
		counter = counter + 1
	return pairedPoints 

def findRoot(pairedPoints , palmCentre , radius):
	counter =0
	pair = []
	for I in pairedPoints:
		p = Point(palmCentre[0],palmCentre[1])
		c = p.buffer(radius).boundary
		l = LineString([I[0],I[2]])
		i = c.intersection(l)
		root = (i.geoms[0].coords[0][0],i.geoms[0].coords[0][1])
		pairs = [I[0],root]
		pair.append(pairs)
		counter = counter + 1
	return pair

		


def calcProp(finger , HS , endAndRoot , palmCentre, counter , HandLength, img):
	#root = ((int)(endAndRoot[counter][1][0]),(int)(endAndRoot[counter][1][1]))
	#tip = ((int)(endAndRoot[counter][0][0]),(int) (endAndRoot[counter][0][1]))
	#cv2.circle(img,root,5,[60,205,195],-1)
	#cv2.circle(img,tip,5,[60,205,195],-1)
	#cv2.circle(img,palmCentre,10,[60,205,195],-1)
	root = endAndRoot[counter][1]
	tip = endAndRoot[counter][0]
	RC =  np.arctan((root[1]-palmCentre[1])/((1.0)*(root[0]-palmCentre[0])))
	RC = (180/3.14)*RC
	RC = HS - RC
	TC =  np.arctan((tip[1]-palmCentre[1])/((1.0)*(tip[0]-palmCentre[0])))
	TC = (180/3.14)*TC
	TC = HS - TC
	c = HS*palmCentre[0] - palmCentre[1]
	distance = (((-1*HS*root[0])+root[1]+c))/((1.0)*(math.sqrt((HS*HS)+1)))
	distance = distance/((1.0)*HandLength)
	prop = (RC , TC , distance)
	return prop

def littleProbability(data):
	littleMean = [40.99,34.12,-51.52]
	littleSd = [7.91,6.36,6.73]
	cons = math.sqrt(np.pi*2)
	prob = 0
	for I in range(0,3):
		po = (-1*((littleMean[I] - data[I])/(2*littleSd[I]))**2) 
		nume = math.exp(po)
		denom = (littleSd[I]*cons)
		p = nume/denom
		prob = prob + p
	return prob

def indexProbability(data):
	indexMean = [-29.26,-22.06,44.06] 
	indexSd = [6.68,6.31,12.16]
	cons = math.sqrt(np.pi*2)
	prob = 0
	for I in range(0,3):
		po = (-1*((indexMean[I] - data[I])/(2*indexSd[I]))**2) 
		nume = math.exp(po)
		denom = (indexSd[I]*cons)
		p = nume/denom
		prob = prob + p
	return prob

def middleProbability(data):
	middleMean = [-6.07,-4.45,10.14]
	middleSd = [6.7,5.92,10.92]
	cons = math.sqrt(np.pi*2)
	prob = 0
	for I in range(0,3):
		po = (-1*((middleMean[I] - data[I])/(2*middleSd[I]))**2) 
		nume = math.exp(po)
		denom = (middleSd[I]*cons)
		p = nume/denom
		prob = prob + p
	return prob

def ringProbability(data):
	ringSd = [6.92,6.27,7.43]
	ringMean = [16.03,12.03,-23.71]
	thumbMean = [-79.89,-67.52,69.45]
	thumbSd = [8.52,5.68,6.6]
	cons = math.sqrt(np.pi*2)
	prob = 0
	for I in range(0,3):
		po = (-1*((ringMean[I] - data[I])/(2*ringSd[I]))**2) 
		nume = math.exp(po)
		denom = (ringSd[I]*cons)
		p = nume/denom
		prob = prob + p
	return prob

def thumbProbability(data):
	thumbMean = [-79.89,-67.52,69.45]
	thumbSd = [8.52,5.68,6.6]
	cons = math.sqrt(np.pi*2)
	prob = 0
	for I in range(0,3):
		po = (-1*((thumbMean[I] - data[I])/(2*thumbSd[I]))**2) 
		nume = math.exp(po)
		denom = (thumbSd[I]*cons)
		p = nume/denom
		prob = prob + p
	return prob

	

def calcProbSum(fingerProperties):
	fingerProbability = []
	littleFinger=[]
	for I in fingerProperties:
		prob = None
		prob = littleProbability(I)
		littleFinger.append(prob)

	fingerProbability.append(littleFinger)

	ringFinger=[]
	for I in fingerProperties:
		prob = None
		prob = ringProbability(I)
		ringFinger.append(prob)

	fingerProbability.append(ringFinger)

	middleFinger=[]
	for I in fingerProperties:
		prob = None
		prob = middleProbability(I)
		middleFinger.append(prob)


	fingerProbability.append(middleFinger)

	indexFinger=[]
	for I in fingerProperties:
		prob = None
		prob = indexProbability(I)
		indexFinger.append(prob)
	fingerProbability.append(indexFinger)

	thumbFinger=[]

	for I in fingerProperties:
		prob = None
		prob = thumbProbability(I)
		thumbFinger.append(prob)
	fingerProbability.append(thumbFinger)

	return fingerProbability