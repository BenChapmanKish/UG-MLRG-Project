#!/usr/bin/python
# 2016-07-12

import sys, os
import numpy as np
import caffe

caffe_path = os.path.expanduser('~/caffe/')
model_dir = caffe_path + 'myModel/'
model_name = sys.argv[1]
if model_name[0] != '/':
	model_name = model_dir + model_name
if len(sys.argv) > 2:
	image_path = sys.argv[2]
else:
	image_path = raw_input('Enter image path: ').replace("'", "").strip()
image_path = os.path.expanduser(image_path)


#load the model
net = caffe.Net(model_dir + 'deploy.prototxt',
                model_name,
                caffe.TEST)

# load input and configure preprocessing
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_mean('data', np.load(caffe_path+'python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1))
transformer.set_transpose('data', (2,0,1))
transformer.set_channel_swap('data', (2,1,0))
transformer.set_raw_scale('data', 255.0)

#note we can change the batch size on-the-fly
#since we classify only one image, we change batch size from 10 to 1
net.blobs['data'].reshape(1,3,227,227)

#load the image in the data layer
im = caffe.io.load_image(image_path)
net.blobs['data'].data[...] = transformer.preprocess('data', im)

#compute
out = net.forward()

# other possibility : out = net.forward_all(data=np.asarray([transformer.preprocess('data', im)]))

#predicted predicted class
print(out['prob'][0])
print out['prob'].argmax()

#print predicted labels
#labels = np.loadtxt(caffe_path+"data/ilsvrc12/synset_words.txt", str, delimiter='\t')
#top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
#print labels[top_k]

