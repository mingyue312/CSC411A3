from PIL import Image
import numpy as np
import glob
import pandas as pd

img_list = glob.glob('../train/*.jpg')

labels = pd.read_csv('../train.csv')
labels.drop(labels.columns[2], axis=1, inplace=True)
labels.drop(labels.columns[0], axis=1, inplace=True)
labels = labels.values

f = open('out.bin', 'wb')
for i in range(0, len(img_list)):
    im = Image.open(img_list[i])
    im = np.array(im)

    r = im[:,:,0].flatten()
    g = im[:,:,1].flatten()
    b = im[:,:,2].flatten()
    label = labels[i]

    out = np.array(list(label) + list(r) + list(g) + list(b), np.uint8)
    #out.tofile("out.bin")
    f.write(out)
