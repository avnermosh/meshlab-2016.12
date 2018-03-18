
#!/usr/bin/python

"""
Calculate attributes of 3d model images:
- image coords
- uv coords
Transform from hugin mosaic
python ~/avner/meshlab/branches/meshlab-2016.12/scripts/calcAttributesOf3dModelImages.py
 --pto_filenname /home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall.pto
"""

import argparse
import subprocess
import glob
import tempfile
import os
import sys
import json
from json import JSONEncoder
#####################################

class Point2d:
    def __init__(self):
	self.x = 0
	self.y = 0

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)



#####################################

class Point:
    def __init__(self):
	self.imageCoords = Point2d()
	self.uvCoords = Point2d()
	# self.worldcoords = Point3d()

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)


        
#####################################

class ImageInfo:
    def __init__(self):
	self.imageIndex = 0
        self.topLeft = Point()
        self.topRight = Point()
        self.bottomLeft = Point()
        self.bottomRight = Point()
        self.center = Point()

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)



#####################################

class MyJsonEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

        
#####################################
        
def calc_uv_coords():
    """
    calc_uv_coords
    """
    print( 'BEG calc_uv_coords' )
    
    originX = 0
    originY = 0
    imageWidth = 4752
    imageHeight = 3168
    numImages = 8

    imagePoints = ''
    for imageIndex in range(numImages):
        imagePoints += '%s %s %s\n' % (imageIndex, originX, originY)
        imagePoints += '%s %s %s\n' % (imageIndex, imageWidth-1, originY)
        imagePoints += '%s %s %s\n' % (imageIndex, originX, imageHeight-1)
        imagePoints += '%s %s %s\n' % (imageIndex, imageWidth-1, imageHeight-1)
        imagePoints += '%s %s %s\n' % (imageIndex, int(imageWidth/2), int(imageHeight/2))

    print( 'imagePoints', imagePoints )

    
    pipe = subprocess.Popen(['pano_trafo', args.pto_filenname], stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)

    trafoOut = (pipe.communicate(input
                                 = imagePoints.encode('utf-8'))[0]).decode('utf-8')

    # print( 'imagePoints', imagePoints )

    splitImagePoints = imagePoints.splitlines()
    # print( 'splitImagePoints', splitImagePoints )
    # print( 'len(splitImagePoints)', len(splitImagePoints) )

    splitTrafoOut = trafoOut.splitlines()
    # print( 'splitTrafoOut', splitTrafoOut )
    # print( 'len(splitTrafoOut)', len(splitTrafoOut) )

    imagesInfo = {}

    for index, inPointStr in enumerate(splitImagePoints):
        projectedPointStr = splitTrafoOut[index]
        # print( 'index', index )
        # print( 'inPointStr', inPointStr )
        inPoint = inPointStr.split()
        # print( 'inPoint', inPoint )
        projectedPoint = projectedPointStr.split()

        imageIndex = inPoint[0]

        if imageIndex not in imagesInfo:
            imagesInfo[imageIndex] = ImageInfo()

        imageInfo = imagesInfo[imageIndex]

        point = Point()
        point.imageCoords.x = int(inPoint[1])
        point.imageCoords.y = int(inPoint[2])
        imageCoords = point.imageCoords

        # point.uvCoords.x = float(projectedPoint[0])
        # point.uvCoords.y = float(projectedPoint[1])
        # print( 'point', point )

        # truncate to 2 decimals after the dot
        point.uvCoords.x = round(float(projectedPoint[0]), 2)
        point.uvCoords.y = round(float(projectedPoint[1]), 2)
        # print( 'point1', point )
        
        
        if (imageCoords.x == 0) and (imageCoords.y == 0):
            imageInfo.topLeft = point
        elif (imageCoords.x == 0) and (imageCoords.y == (imageHeight-1)):
            imageInfo.topRight = point
        elif (imageCoords.x == (imageWidth-1)) and (imageCoords.y == 0):
            imageInfo.bottomLeft = point
        elif (imageCoords.x == (imageWidth-1)) and (imageCoords.y == (imageHeight-1)):
            imageInfo.bottomRight = point
        elif (imageCoords.x == int(imageWidth/2)) and (imageCoords.y == int(imageHeight/2)):
            imageInfo.center = point
        else:
            raise AssertionError("foo")

        imagesInfo[imageIndex] = imageInfo

    # M-x json-pretty-print-buffer
    with open(args.out_attributes_filename, 'w') as outfile:
        # json.dump(imagesInfo.values(), outfile, cls=MyJsonEncoder)
        json.dump(imagesInfo.values(), outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

    print( 'END calc_uv_coords' )

    return


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Top level arguments", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--pto_filenname",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall.pto",
                        help="The name of the panorama file")

    parser.add_argument("--out_attributes_filename",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall_image_attributes.json",
                        help="The name wall-images-attributes file")
    
    args = parser.parse_args()

    if calc_uv_coords() != 0:
        sys.exit(1)
