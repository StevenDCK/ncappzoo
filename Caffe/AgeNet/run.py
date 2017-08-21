#! /usr/bin/env python3

from mvnc import mvncapi as mvnc
import sys
import numpy
import cv2
import time
import csv
import os
import sys


def execute_graph(blob,img):
	mvnc.SetGlobalOption(mvnc.GlobalOption.LOGLEVEL, 2)
	devices = mvnc.EnumerateDevices()
	if len(devices) == 0:
		print('No devices found')
		quit()
	device = mvnc.Device(devices[0])
	device.OpenDevice()
	opt = device.GetDeviceOption(mvnc.DeviceOption.OPTIMISATIONLIST)
	with open(blob, mode='rb') as f:
		blob = f.read()
	graph = device.AllocateGraph(blob)
	graph.SetGraphOption(mvnc.GraphOption.ITERATIONS, 1)
	iterations = graph.GetGraphOption(mvnc.GraphOption.ITERATIONS)
	graph.LoadTensor(img.astype(numpy.float16), 'user object')
	output, userobj = graph.GetResult()
	graph.DeallocateGraph()
	device.CloseDevice()
	return output,userobj

#if len(sys.argv) != 2:
#	print ("Usage: enter 1 for age, 2 for gender")
#	sys.exit()
#if sys.argv[1]=='1':
network="age"
#elif sys.argv[1]=='2':
#	network='gender'
#else:
#	print ("Usage: enter 1 for age, 2 for gender")
#	sys.exit()

# open the network blob files
blob='graph'

# categories for age and gender
age_list=['0-2','4-6','8-12','15-20','25-32','38-43','48-53','60-100']
gender_list=['Male','Female']

# read in and pre-process the image:
ilsvrc_mean = numpy.load('age_gender_mean.npy').mean(1).mean(1) #loading the mean file
dim=(227,227)
os.system('wget -O image.jpg -N http://vis-www.cs.umass.edu/lfw/images/Talisa_Bratt/Talisa_Bratt_0001.jpg')
img = cv2.imread('./image.jpg')
img=cv2.resize(img,dim)
img = img.astype(numpy.float32)
img[:,:,0] = (img[:,:,0] - ilsvrc_mean[0])
img[:,:,1] = (img[:,:,1] - ilsvrc_mean[1])
img[:,:,2] = (img[:,:,2] - ilsvrc_mean[2])

#execute the network with the input image on the NCS
output,userobj=execute_graph(blob,img)
print('\n------- predictions --------')
order = output.argsort()
last = len(order)-1
predicted=int(order[last])
if network=='gender':
	print('the predicted gender is ' + gender_list[predicted] + ' with confidence of %3.1f%%' % (100.0*output[predicted]))
else:
	print('the age range is ' + age_list[predicted] + ' with confidence of %3.1f%%' % (100.0*output[predicted]))
