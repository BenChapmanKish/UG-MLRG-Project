#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-12

# Sorts the list of images and their values by the image filename
import re

def num(x):
	return int(re.sub(r"[^0-9]+", '', x))

f=open('frp-original.txt')
n=open('frp.txt','w')
lines=f.readlines()
f.close()
lines.sort(key=lambda x: num(x.split()[1]))
for l in lines:
	n.write(l)
n.close()
