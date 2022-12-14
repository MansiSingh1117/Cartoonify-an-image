# -*- coding: utf-8 -*-
"""standalone_cartoonify.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1f13M5w_KjmsIuaOq5M9q4dNBPOkZJuz3

Nowadays many different apps are available for the cartoonification of an image. The main aim of this project is not to simply build another tool for users to turn their favorite images into cartoon drawings but to draw their attention towards the coding side of it and how easily one can make their own program after learning the basics.

Here, we make use of OpenCV to convert an image into it’s cartoon form.
"""

import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import imageio

"""**Read Image**"""

ImagePath='/content/natalie.jpg'
img1=cv2.imread(ImagePath)
if img1 is None:
        print("Can not find any image. Choose appropriate file")
        sys.exit()
img1=cv2.cvtColor(img1,cv2.COLOR_BGR2RGB)

img1g=cv2.cvtColor(img1,cv2.COLOR_RGB2GRAY)

#Displaying all the images
plt.imshow(img1)
plt.axis("off")
plt.title("Image 1 - original")
plt.show()

plt.imshow(img1g,cmap='gray')
plt.axis("off")
plt.title("Image 1 - grayscale")
plt.show()

"""We used **Bilateral Blurring** as it performs noise reduction while preserving the edges in the image.
It replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels. This weight can be based on a Gaussian distribution. But the difference being that the weights depend not only on Euclidean distance of pixels, but also on the color intensity which preserves the sharp edges.
"""

#Bilateral Blurring
img1b=cv2.bilateralFilter(img1g,3,75,75)
plt.imshow(img1b,cmap='gray')
plt.axis("off")
plt.title("AFTER BILATERAL BLURRING")
plt.show()

"""The next step is to create the edge mask of the image. To do so, we make use of the adaptive threshold function.

**Adaptive thresholding** is the method where the threshold value is calculated for smaller regions and therefore, there will be different threshold values for different regions.
"""

#Creating edge mask
edges=cv2.adaptiveThreshold(img1b,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,3)
plt.imshow(edges,cmap='gray')
plt.axis("off")
plt.title("Edge Mask")
plt.show()

"""**Erosion —**

Erodes away the boundaries of the foreground object
Used to diminish the features of an image.

**Dilation —**

Increases the object area
Used to accentuate features

Performing erosion followed by dilation is called opening. Performing an opening operation allows us to remove small blobs from an image.Erosion removes the small blobs and dilation regrows the size of the eroded target object.
"""

#Eroding and Dilating
kernel=np.ones((1,1),np.uint8)
img1e=cv2.erode(img1b,kernel,iterations=3)
img1d=cv2.dilate(img1e,kernel,iterations=3)
plt.imshow(img1d,cmap='gray')
plt.axis("off")
plt.title("AFTER ERODING AND DILATING")
plt.show()

"""### COLOR QUANTIZATION
It is a process that reduces the number of distinct colors used in an image, provided that the new image should be as visually similar as possible to the original image. In simpler terms, it is the quantization of color spaces. 


K means Clustering 

It groups similar data points together to discover the underlying patterns. K means algorithm identifies ‘K’ centroids and then allocates every data point to the nearest cluster, while keeping the centroids as small as possible. The ‘means’ in ‘**K means**’ refers to averaging the data (finding the centroid).

OpenCV has an inbuilt function to directly perform k means clustering
"""

#Clustering - (K-MEANS)
imgf=np.float32(img1).reshape(-1,3)
criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,20,1.0)
compactness,label,center=cv2.kmeans(imgf,5,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
center=np.uint8(center)
final_img=center[label.flatten()]
final_img=final_img.reshape(img1.shape)

final=cv2.bitwise_and(final_img,final_img,mask=edges)
plt.imshow(final,cmap='gray')
plt.axis("off")
plt.savefig('output1', bbox_inches='tight')

plt.show()

"""# Downloading the pretrained models."""

! mkdir pretrained_models
! cd pretrained_models && wget "http://vllab1.ucmerced.edu/~yli62/CartoonGAN/pytorch_pth/Hayao_net_G_float.pth"

! cd pretrained_models && wget "http://vllab1.ucmerced.edu/~yli62/CartoonGAN/pytorch_pth/Hosoda_net_G_float.pth"

! cd pretrained_models && wget "http://vllab1.ucmerced.edu/~yli62/CartoonGAN/pytorch_pth/Paprika_net_G_float.pth"

! cd pretrained_models && wget "http://vllab1.ucmerced.edu/~yli62/CartoonGAN/pytorch_pth/Shinkai_net_G_float.pth"

"""# Lets test the models"""

# Commented out IPython magic to ensure Python compatibility.
# %config Completer.use_jedi = False

# %load_ext autoreload
# %autoreload 2

import sys
sys.path.append("../")
from io import BytesIO

"""## Our transformer model"""

# networks/Transformer.py

import torch
import torch.nn as nn
import torch.nn.functional as F


class Transformer(nn.Module):
    def __init__(self):
        super(Transformer, self).__init__()
        #
        self.refpad01_1 = nn.ReflectionPad2d(3)
        self.conv01_1 = nn.Conv2d(3, 64, 7)
        self.in01_1 = InstanceNormalization(64)
        # relu
        self.conv02_1 = nn.Conv2d(64, 128, 3, 2, 1)
        self.conv02_2 = nn.Conv2d(128, 128, 3, 1, 1)
        self.in02_1 = InstanceNormalization(128)
        # relu
        self.conv03_1 = nn.Conv2d(128, 256, 3, 2, 1)
        self.conv03_2 = nn.Conv2d(256, 256, 3, 1, 1)
        self.in03_1 = InstanceNormalization(256)
        # relu

        # res block 1
        self.refpad04_1 = nn.ReflectionPad2d(1)
        self.conv04_1 = nn.Conv2d(256, 256, 3)
        self.in04_1 = InstanceNormalization(256)
        # relu
        self.refpad04_2 = nn.ReflectionPad2d(1)
        self.conv04_2 = nn.Conv2d(256, 256, 3)
        self.in04_2 = InstanceNormalization(256)
        # + input

        # res block 2
        self.refpad05_1 = nn.ReflectionPad2d(1)
        self.conv05_1 = nn.Conv2d(256, 256, 3)
        self.in05_1 = InstanceNormalization(256)
        # relu
        self.refpad05_2 = nn.ReflectionPad2d(1)
        self.conv05_2 = nn.Conv2d(256, 256, 3)
        self.in05_2 = InstanceNormalization(256)
        # + input

        # res block 3
        self.refpad06_1 = nn.ReflectionPad2d(1)
        self.conv06_1 = nn.Conv2d(256, 256, 3)
        self.in06_1 = InstanceNormalization(256)
        # relu
        self.refpad06_2 = nn.ReflectionPad2d(1)
        self.conv06_2 = nn.Conv2d(256, 256, 3)
        self.in06_2 = InstanceNormalization(256)
        # + input

        # res block 4
        self.refpad07_1 = nn.ReflectionPad2d(1)
        self.conv07_1 = nn.Conv2d(256, 256, 3)
        self.in07_1 = InstanceNormalization(256)
        # relu
        self.refpad07_2 = nn.ReflectionPad2d(1)
        self.conv07_2 = nn.Conv2d(256, 256, 3)
        self.in07_2 = InstanceNormalization(256)
        # + input

        # res block 5
        self.refpad08_1 = nn.ReflectionPad2d(1)
        self.conv08_1 = nn.Conv2d(256, 256, 3)
        self.in08_1 = InstanceNormalization(256)
        # relu
        self.refpad08_2 = nn.ReflectionPad2d(1)
        self.conv08_2 = nn.Conv2d(256, 256, 3)
        self.in08_2 = InstanceNormalization(256)
        # + input

        # res block 6
        self.refpad09_1 = nn.ReflectionPad2d(1)
        self.conv09_1 = nn.Conv2d(256, 256, 3)
        self.in09_1 = InstanceNormalization(256)
        # relu
        self.refpad09_2 = nn.ReflectionPad2d(1)
        self.conv09_2 = nn.Conv2d(256, 256, 3)
        self.in09_2 = InstanceNormalization(256)
        # + input

        # res block 7
        self.refpad10_1 = nn.ReflectionPad2d(1)
        self.conv10_1 = nn.Conv2d(256, 256, 3)
        self.in10_1 = InstanceNormalization(256)
        # relu
        self.refpad10_2 = nn.ReflectionPad2d(1)
        self.conv10_2 = nn.Conv2d(256, 256, 3)
        self.in10_2 = InstanceNormalization(256)
        # + input

        # res block 8
        self.refpad11_1 = nn.ReflectionPad2d(1)
        self.conv11_1 = nn.Conv2d(256, 256, 3)
        self.in11_1 = InstanceNormalization(256)
        # relu
        self.refpad11_2 = nn.ReflectionPad2d(1)
        self.conv11_2 = nn.Conv2d(256, 256, 3)
        self.in11_2 = InstanceNormalization(256)
        # + input

        ##------------------------------------##
        self.deconv01_1 = nn.ConvTranspose2d(256, 128, 3, 2, 1, 1)
        self.deconv01_2 = nn.Conv2d(128, 128, 3, 1, 1)
        self.in12_1 = InstanceNormalization(128)
        # relu
        self.deconv02_1 = nn.ConvTranspose2d(128, 64, 3, 2, 1, 1)
        self.deconv02_2 = nn.Conv2d(64, 64, 3, 1, 1)
        self.in13_1 = InstanceNormalization(64)
        # relu
        self.refpad12_1 = nn.ReflectionPad2d(3)
        self.deconv03_1 = nn.Conv2d(64, 3, 7)
        # tanh

    def forward(self, x):
        y = F.relu(self.in01_1(self.conv01_1(self.refpad01_1(x))))
        y = F.relu(self.in02_1(self.conv02_2(self.conv02_1(y))))
        t04 = F.relu(self.in03_1(self.conv03_2(self.conv03_1(y))))

        ##
        y = F.relu(self.in04_1(self.conv04_1(self.refpad04_1(t04))))
        t05 = self.in04_2(self.conv04_2(self.refpad04_2(y))) + t04

        y = F.relu(self.in05_1(self.conv05_1(self.refpad05_1(t05))))
        t06 = self.in05_2(self.conv05_2(self.refpad05_2(y))) + t05

        y = F.relu(self.in06_1(self.conv06_1(self.refpad06_1(t06))))
        t07 = self.in06_2(self.conv06_2(self.refpad06_2(y))) + t06

        y = F.relu(self.in07_1(self.conv07_1(self.refpad07_1(t07))))
        t08 = self.in07_2(self.conv07_2(self.refpad07_2(y))) + t07

        y = F.relu(self.in08_1(self.conv08_1(self.refpad08_1(t08))))
        t09 = self.in08_2(self.conv08_2(self.refpad08_2(y))) + t08

        y = F.relu(self.in09_1(self.conv09_1(self.refpad09_1(t09))))
        t10 = self.in09_2(self.conv09_2(self.refpad09_2(y))) + t09

        y = F.relu(self.in10_1(self.conv10_1(self.refpad10_1(t10))))
        t11 = self.in10_2(self.conv10_2(self.refpad10_2(y))) + t10

        y = F.relu(self.in11_1(self.conv11_1(self.refpad11_1(t11))))
        y = self.in11_2(self.conv11_2(self.refpad11_2(y))) + t11
        ##

        y = F.relu(self.in12_1(self.deconv01_2(self.deconv01_1(y))))
        y = F.relu(self.in13_1(self.deconv02_2(self.deconv02_1(y))))
        y = torch.tanh(self.deconv03_1(self.refpad12_1(y)))

        return y


class InstanceNormalization(nn.Module):
    def __init__(self, dim, eps=1e-9):
        super(InstanceNormalization, self).__init__()
        self.scale = nn.Parameter(torch.FloatTensor(dim))
        self.shift = nn.Parameter(torch.FloatTensor(dim))
        self.eps = eps
        self._reset_parameters()

    def _reset_parameters(self):
        self.scale.data.uniform_()
        self.shift.data.zero_()

    def __call__(self, x):
        n = x.size(2) * x.size(3)
        t = x.view(x.size(0), x.size(1), n)
        mean = torch.mean(t, 2).unsqueeze(2).unsqueeze(3).expand_as(x)
        # Calculate the biased var. torch.var returns unbiased var
        var = torch.std(t, 2) ** 2
        var = var.unsqueeze(2).unsqueeze(3).expand_as(x) * (
            (n - 1) / torch.FloatTensor([n])
        )
        scale_broadcast = self.scale.unsqueeze(1).unsqueeze(1).unsqueeze(0)
        scale_broadcast = scale_broadcast.expand_as(x)
        shift_broadcast = self.shift.unsqueeze(1).unsqueeze(1).unsqueeze(0)
        shift_broadcast = shift_broadcast.expand_as(x)
        out = (x - mean) / torch.sqrt(var + self.eps)
        out = out * scale_broadcast + shift_broadcast
        return out

# test_from_code.py

import time
import os

import numpy as np
from PIL import Image

import torch
import torchvision.transforms as transforms
from torch.autograd import Variable

def transform(models, style, input, load_size=450, gpu=-1):
  model = models[style]

  if (gpu > -1):
    model.cuda()
  else:
    model.float()
  
  input_image = Image.open(input).convert("RGB")
  h, w = input_image.size

  ratio = h * 1.0 / w

  if ratio > 1:
    h =  load_size
    w = int(h * 1.0 / ratio)
  else:
    w = load_size
    h = int(w * ratio)
  
  input_image=  input_image.resize((h, w), Image.BICUBIC)
  input_image = np.asarray(input_image)

  input_image = input_image[:,:,[2,1,0]]
  input_image = transforms.ToTensor()(input_image).unsqueeze(0)

  input_image = -1 + 2 * input_image

  if gpu > -1:
    input_image = Variable(input_image).cuda()
  else:
    ipnut_image = Variable(input_image).float()
  
  t0 = time.time()
  print("input shape", input_image.shape)

  with torch.no_grad():
    output_image = model(input_image)[0]
  
  print("inference time took ", {time.time() - t0}," s")

  output_image = output_image[[2,1,0],:,:]
  output_image = output_image.data.cpu().float() * 0.5 + 0.5

  output_image = output_image.numpy()

  output_image = np.uint8(output_image.transpose(1,2,0) * 255)
  output_image = Image.fromarray(output_image)

  return output_image

import base64
import requests
import torch
# import os
# import numpy as np
import argparse
# from PIL import Image
# import torchvision.transforms as transforms
# from torch.autograd import Variable
import torchvision.utils as vutils
# from network.Transformer import Transformer

from tqdm import tqdm_notebook
# from test_from_code import transform

styles = ["Hosoda", "Hayao", "Shinkai", "Paprika"]

models = {}

for style in tqdm_notebook(styles):
  model = Transformer()
  model.load_state_dict(torch.load(os.path.join("./pretrained_models", style + '_net_G_float.pth')))
  model.eval()
  models[style] = model

! wget -O natalie.jpg "https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F44%2F2020%2F10%2F22%2FGettyImages-1206912568-2000.jpg&q=85"

path = "./natalie.jpg"

img = Image.open(path)
img

style = "Shinkai"

load_size = 450

# Commented out IPython magic to ensure Python compatibility.
# %%time
# output300 = transform(models, style, path, load_size)

output300