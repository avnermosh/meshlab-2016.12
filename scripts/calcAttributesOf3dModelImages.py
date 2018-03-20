
#!/usr/bin/python

"""
Calculate attributes of 3d model images:
- image coords
- uv coords
Transform from hugin mosaic
python ~/avner/meshlab/branches/meshlab-2016.12/scripts/calcAttributesOf3dModelImages.py
 --pto_filename /home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall.pto
"""

import argparse
import subprocess
import glob
import tempfile
import os
import sys
import json
from json import JSONEncoder
from imageInfo import WallInfo, ImageInfo, Point, Point2d, MyJsonEncoder
import re
import pickle


#####################################

def extract_images_info_from_pto_file():
    """
    place holder
    """
    # print( 'BEG extract_images_info_from_pto_file' )

    pattern1  = '^p '
    pattern2  = '^i '
    pattern3  = '\ w(\d+)\ h(\d+)\ '

    wallImageInfo = ImageInfo()
    imagesInfo = []
    imageIndex = 0

    # populate imageInfos with multiple imageInfo

    # Make sure file gets closed after being iterated
    with open(args.pto_filename, 'r') as f:
        # Read the file contents and generate a list with each line
        lines = f.readlines()

        # Iterate each line
        for line in lines:

            # Regex applied to each line
            match = re.search(pattern1, line)
            if match:
                # print( 'line1', line )

                match = re.search(pattern3, line)
                if match:
                    # print( 'line1a', line )
                    numGroups = match.groups()
                    # print( 'numGroups1', numGroups )
                    width = match.group(1)
                    # print( 'width1', width )
                    height = match.group(2)
                    # print( 'height1', height )

                    wallImageInfo.imageWidth = int(width)
                    wallImageInfo.imageHeight = int(height)


            # Regex applied to each line
            match = re.search(pattern2, line)
            if match:
                # Make sure to add \n to display correctly when we write it back
                # print( 'line2', line )

                match = re.search(pattern3, line)
                if match:
                    # print( 'line2a', line )
                    numGroups = match.groups()
                    # print( 'numGroups2', numGroups )
                    width = match.group(1)
                    # print( 'width2', width )
                    height = match.group(2)
                    # print( 'height2', height )

                    imageInfo = ImageInfo()
                    imageInfo.imageIndex = imageIndex
                    imageIndex += 1
                    imageInfo.imageWidth = int(width)
                    imageInfo.imageHeight = int(height)
                    imagesInfo.append(imageInfo)



    # print( 'wallImageInfo', wallImageInfo )
    # print( 'imagesInfo', imagesInfo )

    return( wallImageInfo, imagesInfo )

#####################################


def calc_uv_coords(wallImageInfo, imagesInfo):
    """
    calc_uv_coords
    """
    print( 'BEG calc_uv_coords' )

    # update points of wallImageInfo with the imageCoords
    wallImageInfo.tlPoint.imageCoords.x = 0
    wallImageInfo.tlPoint.imageCoords.y = 0

    wallImageInfo.trPoint.imageCoords.x = wallImageInfo.imageWidth-1
    wallImageInfo.trPoint.imageCoords.y = wallImageInfo.originY

    wallImageInfo.blPoint.imageCoords.x = wallImageInfo.originX
    wallImageInfo.blPoint.imageCoords.y = wallImageInfo.imageHeight-1

    wallImageInfo.brPoint.imageCoords.x = wallImageInfo.imageWidth-1
    wallImageInfo.brPoint.imageCoords.y = wallImageInfo.imageHeight-1

    wallImageInfo.centerPoint.imageCoords.x = int(wallImageInfo.imageWidth/2)
    wallImageInfo.centerPoint.imageCoords.y = int(wallImageInfo.imageHeight/2)




    # update points of imageInfo with the imageCoords

    imagePoints = ''
    for imageInfo in imagesInfo:
        imageInfo.tlPoint.imageCoords.x = 0
        imageInfo.tlPoint.imageCoords.y = 0
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.tlPoint.imageCoords.x, imageInfo.tlPoint.imageCoords.y)

        # typeOfimageInfo = type(imageInfo.imageWidth)
        # print( 'typeOfimageInfo', typeOfimageInfo )

        # typeOfimageCoordsX = type(imageInfo.trPoint.imageCoords.x)
        # print( 'typeOfimageCoordsX', typeOfimageCoordsX )

        imageInfo.trPoint.imageCoords.x = imageInfo.imageWidth-1
        imageInfo.trPoint.imageCoords.y = imageInfo.originY
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.trPoint.imageCoords.x, imageInfo.trPoint.imageCoords.y)

        imageInfo.blPoint.imageCoords.x = imageInfo.originX
        imageInfo.blPoint.imageCoords.y = imageInfo.imageHeight-1
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.blPoint.imageCoords.x, imageInfo.blPoint.imageCoords.y)

        imageInfo.brPoint.imageCoords.x = imageInfo.imageWidth-1
        imageInfo.brPoint.imageCoords.y = imageInfo.imageHeight-1
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.brPoint.imageCoords.x, imageInfo.brPoint.imageCoords.y)

        imageInfo.centerPoint.imageCoords.x = int(imageInfo.imageWidth/2)
        imageInfo.centerPoint.imageCoords.y = int(imageInfo.imageHeight/2)
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.centerPoint.imageCoords.x, imageInfo.centerPoint.imageCoords.y)

    print( 'imagePoints', imagePoints )

    pipe = subprocess.Popen(['pano_trafo', args.pto_filename], stdout=subprocess.PIPE,
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

    for inPointIndex, inPointStr in enumerate(splitImagePoints):

        inPointArr = inPointStr.split()

        projectedPointStr = splitTrafoOut[inPointIndex]
        projectedPoint = projectedPointStr.split()

        imageIndex = int(inPointArr[0])
        # print( 'imageIndex', imageIndex )

        if ((imageIndex<0) or (imageIndex>=len(imagesInfo))):
            print( 'imageIndex', imageIndex )
            raise AssertionError("imageIndex not in imagesInfo")

        imageInfo = imagesInfo[imageIndex]

        # update points of imageInfo with the uvCoords
        point = Point()
        point.imageCoords.x = int(inPointArr[1])
        point.imageCoords.y = int(inPointArr[2])
        imageCoords = point.imageCoords

        # truncate to 2 decimals after the dot
        point.uvCoords.x = round(float(projectedPoint[0]), 2)
        point.uvCoords.y = round(float(projectedPoint[1]), 2)

        point.uvCoordsNormalized.x = round(point.uvCoords.x / wallImageInfo.imageWidth, 2)
        point.uvCoordsNormalized.y = round(point.uvCoords.y / wallImageInfo.imageHeight, 2)

        # print( 'point1', point )

        # __eq__
        if (point.imageCoords == imageInfo.tlPoint.imageCoords):
            imageInfo.tlPoint = point
        elif (point.imageCoords == imageInfo.trPoint.imageCoords):
            imageInfo.trPoint = point
        elif (point.imageCoords == imageInfo.blPoint.imageCoords):
            imageInfo.blPoint = point
        elif (point.imageCoords == imageInfo.brPoint.imageCoords):
            imageInfo.brPoint = point
        elif (point.imageCoords == imageInfo.centerPoint.imageCoords):
            imageInfo.centerPoint = point
        else:
            raise AssertionError("Invalid imageCoords")

        imagesInfo[imageIndex] = imageInfo

    wallInfo = WallInfo()
    wallInfo.wallImageInfo = wallImageInfo
    wallInfo.imagesInfo = imagesInfo

    return wallInfo


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Top level arguments", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--pto_filename",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall.pto",
                        help="The name of the panorama file")

    parser.add_argument("--wall_attributes_filename",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall_image_attributes.json",
                        help="The name wall-images-attributes file")

    args = parser.parse_args()

    ( wallImageInfo, imagesInfo ) = extract_images_info_from_pto_file()

    # typeOfimagesInfo = type(imagesInfo)
    # print( 'typeOfimagesInfo', typeOfimagesInfo )
    # sys.exit(1)

    # print( 'wallImageInfo2', wallImageInfo )
    # print( 'imagesInfo2', imagesInfo )

    wallInfo = calc_uv_coords(wallImageInfo, imagesInfo)

    # M-x json-pretty-print-buffer
    json_wall_attributes_filename = args.wall_attributes_filename


    (filename_without_extension, filename_suffix) = os.path.splitext(json_wall_attributes_filename)
    print( 'filename_without_extension', filename_without_extension )
    print( 'filename_suffix', filename_suffix )

    pickle_wall_attributes_filename = filename_without_extension + '.pickle'
    print( 'pickle_wall_attributes_filename', pickle_wall_attributes_filename )

    with open(json_wall_attributes_filename, 'w') as outfile:
        json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

    # print( 'wallInfo', wallInfo )
    # print( '' )
    # print( '' )
    # print( '' )
    # print( '' )
    # print( '' )

    with open(pickle_wall_attributes_filename, 'w') as outfile:
        pickle.dump(wallInfo, outfile)

    print( 'END Main' )

