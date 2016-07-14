#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-13

# Prepares the AFLW dataset for use with caffe
from PIL import Image
import sys, os, random, time, datetime

def notface(c, nx, ny):
	crop_rect = (nx, ny, w+nx, h+ny)
	cropped_img = img.crop(crop_rect)
	#cropped_img.thumbnail(resize, Image.ANTIALIAS)
	if i % 10 == 0:
		filename = odir + '/val/' + face + c + fne
		val.write(filename+' 0\n')
	else:
		filename = odir + '/train/' + face + c + fne
		train.write(filename+' 0\n')
	cropped_img.save(filename, format="JPEG")
	if i % 10 == 0:
		sys.stdout.write('\033[33m'+filename+'\033[0m\n')
	else:
		sys.stdout.write('\033[35m'+filename+'\033[0m\n')

resize = (227, 227)
tdir=os.path.expanduser('~/aflw')
odir=os.path.expanduser('~/caffe/myModel')
#imgset = list(sys.argv[1]) # 0,2,3
if len(sys.argv)>1:
	offset = int(sys.argv[1])
else:
	offset = 0
start = time.time()

if os.path.isfile(odir+'/train.txt'):
	os.remove(odir+'/train.txt')
train=open(odir+'/train.txt','a')
if os.path.isfile(odir+'/val.txt'):
	os.remove(odir+'/val.txt')
val=open(odir+'/val.txt','a')

# frp.txt is a list of the images and their properties
with open(tdir+'/frp.txt') as f:
	lines=[l.split() for l in f.readlines()]
	#lines=[l for l in lines if l[1][0] in imgset]
	lenlines=len(lines)
	for i in xrange(offset, lenlines):
		l=lines[i]
		face=l[0] # face id
		imgpath=l[1] # absolute path to image
		x=int(l[2]) # face rect x offset
		y=int(l[3]) # face rect y offset
		w=int(l[4]) # face rect width
		h=int(l[5]) # face rect height

		try:
			img = Image.open(imgpath)
			width, height = img.size
			# shift the face rect by random margins
			rx = x + random.randint(-w/4, w/4)
			ry = y + random.randint(-h/4, h/4)
			crop_rect = (rx, ry, w+rx, h+ry)
			cropped_img = img.crop(crop_rect)
			#cropped_img.thumbnail(resize, Image.ANTIALIAS)
			fne = '.jpg' #imgpath[imgpath.index('.'):]

			if i % 10 == 0:
				filename = odir + '/val/' + face + fne
				val.write(filename+' 1\n')
			else:
				filename = odir + '/train/' + face + fne
				train.write(filename+' 1\n')

			cropped_img.save(filename, format="JPEG")
			sys.stdout.write(imgpath+' '+face+'\n')
			if i % 10 == 0:
				sys.stdout.write('\033[33m'+filename+'\033[0m\n')
			else:
				sys.stdout.write('\033[35m'+filename+'\033[0m\n')

			# get samples of parts of images that aren't faces
			# images with multiple faces are excluded for simplicity
			# shift the face rect by random amounts and generate
			#    up to two non-face images
			if (0 < i < lenlines - 1) and lines[i-1][1] != imgpath and lines[i+1][1] != imgpath:
				if w*3/2 < x:
					notface('a', x - w*3/2, y + random.randint(-h/5, h/5))
				elif w*3/2 < width-w-x:
					notface('a', x + w*3/2, y + random.randint(-h/5, h/5))
				if h*3/2 < y:
					notface('b', x + random.randint(-w/5, w/5), y - h*3/2)
				elif h*3/2 < height-h-y:
					notface('b', x + random.randint(-w/5, w/5), y + h*3/2)

		# a single image in the whole aflw dataset caused this error
		except IOError:
			sys.stdout.write('\033[31m'+imgpath+' '+face+'\033[0m\n')

		te = (time.time() - start)
		te_m, te_s = divmod(te, 60)
		eta = int((te / (i-offset+1.0)) * (lenlines-1-i))
		eta_m, eta_s = divmod(eta, 60)
		# track time elapsed and estimated time remaining
		sys.stdout.write('\033[36m'+str(i)+'\033[0m/\033[34m'+str(lenlines-1)+'\033[0m (\033[32m'+str(i * 100 / (lenlines-1))+'%\033[0m)\n')
		sys.stdout.write('TE: '+str(int(te_m))+'m'+str(int(te_s))+'s  ETA: '+str(int(eta_m))+'m'+str(int(eta_s))+'s\n\n')
