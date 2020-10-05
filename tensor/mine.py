#!/usr/bin/python
# ***************************************************************************
# * @File:       mine.py
# *
# * @Brief:      mines log and outputs time & RMS information
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************
import sys

fp = open(sys.argv[1],'r')
print('Output, Regressor, Estimator, Time(s), RMS')
while True:
	line = fp.readline().strip()
	if line=='':
		break
	opt = ''
	regressor = ''
	tgt = ''
	if 'jpt_hard' in line:
		l = line.split()
		opt = l[0]
		regressor = l[1]
		tgt = l[2]
	else:
		continue
	
	line = fp.readline()
	if 'RMS error' in line:
		l = line.split()
		sigma = float(l[-1].strip('$'))
	else:
		continue
	line = fp.readline()
	if 'Train' in line:
		l = line.split()
		t = float(l[-1])
	else:
		continue
	line = fp.readline()
	print "%s, %s, %s, %5.2f, %f" % (tgt,regressor,opt,t,sigma)

fp.close()
		

