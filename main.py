from __future__ import print_function
import errno
import os
import sys
import subprocess

import numpy as np
import cv2

from glob import glob
import processing as proc


def readImages(image_dir):
    extensions = ['bmp', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'jpeg',
                  'jpg', 'jpe', 'jp2', 'tiff', 'tif', 'png']

    search_paths = [os.path.join(image_dir, '*.' + ext) for ext in extensions]
    image_files = sorted(reduce(list.__add__, map(glob, search_paths)))
    images = [cv2.imread(f, cv2.IMREAD_UNCHANGED | cv2.IMREAD_COLOR)
              for f in image_files]

    bad_read = any([img is None for img in images])
    if bad_read:
        raise RuntimeError(
            "Reading one or more files in {} failed - aborting."
            .format(image_dir))

    return image_files, images

    
def toonifyImage(inputImage, blurriness, thickness):
    smoothImage = proc.SmoothImages(inputImage, 7, blurriness)
    edgeMask = proc.GetEdgeMask(smoothImage)
    dilatedEdges = proc.EdgesDilation(edgeMask, thickness)
    outputImage = proc.Toonify(smoothImage, dilatedEdges)
    
    return outputImage
    

def sketchifyImage(inputImage, kSize, darkness):
    grayScaleImage = proc.getGrayScale(inputImage)
    negativeImage = proc.getNegative(grayScaleImage)
    sketchMask = proc.getSketchMask(negativeImage, kSize)
    outputImage = proc.Sketchify(grayScaleImage, sketchMask, darkness)

    return outputImage
    
    
if __name__ == "__main__":
    print(__doc__)

    try:
        if (sys.argv[1] == '-t'):
            type = 'toon'
        else:
            type = 'sketch'
            
        imageFile = sys.argv[2]
        
    except:
        type = 'sketch'
        imageFile = 0

    def nothing(*arg):
        pass

    blurriness = 15
    thickness = 4
    kSize = 151 # 11
    darkness = 300 # 258

    image = cv2.imread(imageFile, cv2.IMREAD_UNCHANGED | cv2.IMREAD_COLOR)

    def updateBlurriness(value):
        blurriness = value
        toonified = toonifyImage(image, blurriness, thickness)
        cv2.imshow('toon', toonified)

    def updateThickness(value):
        thickness = value
        toonified = toonifyImage(image, blurriness, thickness)
        cv2.imshow('toon', toonified)

    def updateKSize(value):
        kSize = value
        if (kSize % 2 == 0):
            kSize += 1 # must be odd
        sketchified = sketchifyImage(image, kSize, darkness)
        cv2.imshow('sketch', sketchified)

    def updateDarkness(value):
        darkness = value
        sketchified = sketchifyImage(image, kSize, darkness)
        cv2.imshow('sketch', sketchified)

    if type == 'toon':
        cv2.namedWindow('toon', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('toon', 1800, 900)
        cv2.createTrackbar('blurriness', 'toon', blurriness, 30, updateBlurriness)
        cv2.createTrackbar('thickness', 'toon', thickness, 10, updateThickness)
        cv2.imshow('toon', image)
        updateBlurriness(blurriness) # initialize
    else:
        cv2.namedWindow('sketch', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('sketch', 1800, 900)
        cv2.createTrackbar('kSize', 'sketch', kSize, 200, updateKSize)
        cv2.createTrackbar('darkness', 'sketch', darkness, 300, updateDarkness)
        cv2.imshow('sketch', image)
        updateKSize(kSize) # initialize

    key = cv2.waitKey(0)      
    
    if (key == ord('s')):
      if (type == 'toon'):
          toonifiedFile = os.path.join(os.path.dirname(imageFile), 'toon_' + os.path.basename(imageFile))
          toonifiedImage = toonifyImage(image, blurriness, thickness)
          cv2.imwrite(toonifiedFile, toonifiedImage)
          subprocess.check_call(["exiftool.exe", "-ProjectionType=equirectangular", toonifiedFile])
      else:
          sketchifiedFile = os.path.join(os.path.dirname(imageFile), 'sketch_' + os.path.basename(imageFile))
          sketchifiedImage = sketchifyImage(image, kSize, darkness)
          cv2.imwrite(sketchifiedFile, sketchifiedImage)
          subprocess.check_call(["exiftool.exe", "-ProjectionType=equirectangular", sketchifiedFile])
      
    cv2.destroyAllWindows()
