#!/usr/bin/env python
#
# Script to plot the contents of a .pix file output
# with splash -o ascii
#
import os
import argparse
from colour.models import RGB_COLOURSPACES
from colour_hdri import tonemapping_operator_Schlick1994
import numpy as np
import matplotlib.pyplot as plt
import sys
import re

def read_header( file ):
    """
      read the x, y and v plot limits from the .pix header lines
    """
    pat = re.compile(r'.*min\s*=\s+(\S+)\s+max\s*=\s+(\S+)')
    fh = open(file, 'r')
    count = 0
    got = 0
    xmin = np.full((3),0.)
    xmax = np.full((3),1.)
    while (count < 10):
       count += 1

       # Get next line from file
       line = fh.readline()

       # if line is empty
       # end of file is reached
       if not line:
          break

       # otherwise match lines like "min = 0.000 max = 1.000"
       if (pat.match(line)):
          [m] = pat.findall(line)
          xmin[got] = m[0]
          xmax[got] = m[1]
          got += 1

    return xmin[2],xmax[2],xmin[1],xmax[1],xmin[0],xmax[0]

def read_pix( file ):
    """
      read the floating point pixel values
    """
    array = np.loadtxt(file)
    return array

def plot_pix( file, saveFile ):
    """
      plot the pixel map with appropriate limits
    """
    xmin,xmax,ymin,ymax,vmin,vmax = read_header(file)
    img = read_pix(file)
    print(file,img.shape)
    plt.imshow(img,cmap='RdBu',origin='lower',vmin=vmin,vmax=vmax,extent=[xmin,xmax,ymin,ymax])
    
    if(saveFile is not None):
        plt.imsave(fname=saveFile,arr=img,cmap='RdBu',origin='lower',vmin=vmin,vmax=vmax)
    else:
        plt.show()

def plot_pix_rgb( file1, file2, file3, saveFile ,tonemap_p, tonemap_cs):
    """
      plot three pixel maps as an RGB image with appropriate limits
    """

    xmin,xmax,ymin,ymax,vmin,vmax = read_header(file1)

    img1 = read_pix(file1)
    print(file1,img1.shape)
    img2 = read_pix(file2)
    print(file2,img2.shape)
    img3 = read_pix(file3)
    print(file3,img3.shape)

    #The images are clipped at the vmin and vmax values of the red channel if tonemapping is not used.
    if(tonemap_p is None):
        img1=np.maximum(np.minimum(img1,vmax),vmin)
        img2=np.maximum(np.minimum(img2,vmax),vmin)
        img3=np.maximum(np.minimum(img3,vmax),vmin)


    imgRGB = np.stack(arrays=[img1,img2,img3],axis=2)

    if(tonemap_p is not None):
        imgRGB=np.maximum(imgRGB,1.0e-99) #Prevents zero values from going into the tonemapping operator.
        imgRGB=tonemapping_operator_Schlick1994(imgRGB,p=tonemap_p[0],colourspace=RGB_COLOURSPACES[tonemap_cs[0]])

    
    imgRGB /= np.max(imgRGB) #Normalizes the pixel values to between 0 and 1.
    plt.imshow(X=imgRGB,origin='lower',extent=[xmin,xmax,ymin,ymax])
    
    if(saveFile is not None):
        plt.imsave(fname=saveFile,arr=np.flip(imgRGB,axis=0))
    else:
        plt.show()
 
 
 
colourspaceList=list(RGB_COLOURSPACES.data.keys())
filenamesHelp = "The input file names. In RGB mode, do not place _r, _g and _b in between the filename and extension in this argument; it will be done automatically once the program is running. Multiple filenames can be used in order to process multiple files (or multiple triplets of red, green and blue channel files)."
rgbHelp = "Turns a triplet of .pix files into an RGB image instead of applying a colourmap to the values of a single .pix file. The filenames for each colour channel are the same except for _r, _g and _b in between the filenames and file extensions. All channels are scaled between the vmin and vmax values of the red channel file unless tonemapping is used."
saveHelp = "Saves the image instead of showing it. The saved files have the same names as that put in the filenames argument but the argument of --save is used to set the file extension (compatible extensions are the ones compatible with the pyplot.savefig method of matplotlib)." 
tonemap_pHelp = "For RGB images compresses the dynamic range for a display (while aiming to retain what the input data would look like to a human eye) using the Schlick1994 tonemapping algorithm from the colour-hdri Python package. The value of this argument sets the value of \"p\" for the algorithm. For details on the algorithm and for a method to estimate an appropriate value of \"p\" see Section 3 and equations 6 and 7 in the paper \"Quantization Techniques for Visualization of High Dynamic Range Pictures\" by Christophe Schlick in 1994."
tonemap_csHelp = "When tonemap_p is set this sets the colourspace of the intended display for viewing. This defaults to sRGB."

argumentParser=argparse.ArgumentParser()
argumentParser.add_argument("filenames",help=filenamesHelp,nargs="+",type=str)
argumentParser.add_argument("--rgb",help=rgbHelp,action="store_true")
argumentParser.add_argument("--save",help=saveHelp,nargs=1,default=None,type=str)
argumentParser.add_argument("--tonemap_p",help=tonemap_pHelp,nargs=1,default=None,type=float)
argumentParser.add_argument("--tonemap_cs",help=tonemap_csHelp,nargs=1,choices=colourspaceList,default=["sRGB"],type=str)


arguments=argumentParser.parse_args()
if(arguments.rgb):
    for currentFilename in arguments.filenames:
        currentFilenameRoot = os.path.splitext(currentFilename)[0]
        file_r = currentFilenameRoot+"_r.pix"
        file_g = currentFilenameRoot+"_g.pix"
        file_b = currentFilenameRoot+"_b.pix"
        fileSave = None if(arguments.save is None) else currentFilenameRoot+(arguments.save)[0]
        plot_pix_rgb(file_r,file_g,file_b,fileSave,arguments.tonemap_p,arguments.tonemap_cs)
else:
    for currentFilename in arguments.filenames:
        currentFilenameRoot = os.path.splitext(currentFilename)[0]
        fileSave = None if(arguments.save is None) else currentFilenameRoot+(arguments.save)[0]
        plot_pix(currentFilename,fileSave)
