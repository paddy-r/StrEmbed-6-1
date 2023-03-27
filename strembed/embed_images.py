# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 12:33:50 2020

@author: prehr
To get all images in folder and embed in script
"""

import os
from time import localtime, strftime
# import glob
from wx.tools.img2py import img2py


# Bundled into method to allow calling within StrEmbed
def embed():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    # print(data_path)
    im_path = os.path.join(data_path, 'images')
    # print(im_path)
    types = ['png', 'bmp']

    # pics = []
    for files in types:
        # files_grabbed.extend(glob.glob(files))
        # pics.extend(glob.glob(os.path.join(im_path, files)))
        pics = [os.path.join(im_path, f) for f in os.listdir(im_path) if f.split(".")[-1] in types]
    # print('Found images:')
    # for pic in pics:
    #     print(pic)

    scr_path = os.path.join(im_path, 'images.py')
    try:
        os.remove(scr_path)
        print('Trying to delete existing images script...', scr_path)
    except:
        print('Existing imaged script not found; script "', os.path.split(scr_path)[-1], '" will be created')

    # Main bit: dumping image data...
    for pic in pics:
        # Get filename only from full path
        _name = os.path.split(pic)[-1]
        img2py(pic, scr_path, append = True, imgName = _name, icon = True)

    # ...then reload and prepend header, as wasn't working properly otherwise
    _time = strftime("%d-%m-%Y %H:%M:%S", localtime())
    header_text = '# HR ' + _time + '\n' \
        + '# Created with "embed_images.py"\n\n' \
        + 'from wx.lib.embeddedimage import PyEmbeddedImage\n' \
        + '\n###############################################################################\n\n'
    with open(scr_path, 'r') as original:
        data = original.read()
    with open(scr_path, 'w') as modified:
        modified.write(header_text + data)


if __name__ == "__main__":
    print('Running "embed_images" as script')
    embed()
