
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
from imageInfo import WallInfo, ImageInfo, Point, Point2d, Point3d, MyJsonEncoder
import re
import pickle


#####################################

def extract_images_info_from_pto_file(wallInfo, pto_filename):
    """
    Extract the following attributes for the following images:
    - overviewImageInfo: 
      -- imageWidth
      -- imageHeight
    - imageInfo
      -- imageIndex
      -- imageWidth
      -- imageHeight
      -- imageFileName
    """

                    
    print( 'BEG extract_images_info_from_pto_file' )
    print( 'pto_filename', pto_filename )
    
    pattern_panorama  = '^p '

    #                                    left,right,top,bottom
    # p f0 w1000 h1539 v53  E7.90689 R0 S177,753,73,1454 n"TIFF_m c:LZW"
    pattern_imageWidth_imageHeight  = '\ w(\d+)\ h(\d+)\ '

    # TBD
    pattern_panoModelWidth_panoModelHeight_roi  = '\ w(\d+)\ h(\d+)\ .*\ S(\d+),(\d+),(\d+),(\d+)\ n".*"'


    pattern_image  = '^i '

    # i w4752 h3168 f0 ... Vd0 Vx0 Vy0  Vm5 n"IMG_6860.JPG"
    pattern_imageWidth_imageHeight_imageName  = '\ w(\d+)\ h(\d+)\ .*\ n"(.*)"'


    overviewImageInfo = ImageInfo()
    imagesInfo = []
    imageIndex = 0

    # populate imageInfos with multiple imageInfo

    # Make sure file gets closed after being iterated
    with open(pto_filename, 'r') as f:
        # Read the file contents and generate a list with each line
        lines = f.readlines()

        # Iterate each line
        for line in lines:

            # Regex applied to each line
            match = re.search(pattern_panorama, line)
            if match:
                # match = re.search(pattern_imageWidth_imageHeight, line)
                match = re.search(pattern_panoModelWidth_panoModelHeight_roi, line)
                if match:
                    print( 'line', line )
                    numGroups = match.groups()
                    # print( 'numGroups', numGroups )
                    panorama_model_width1 = match.group(1)
                    panorama_model_height1 = match.group(2)
                    left = match.group(3)
                    right = match.group(4)
                    top = match.group(5)
                    bottom = match.group(6)

                    print( 'left', left )
                    print( 'right', right )
                    print( 'top', top )
                    print( 'bottom', bottom )
                    overviewImageInfo.imageWidth = int(right)-int(left)
                    overviewImageInfo.imageHeight = int(bottom)-int(top)

                    # i w4752 h3168 f0 v=0 Ra=0 Rb=0 Rc=0 Rd=0 Re=0 Eev7.55524178718839 Er1.08207949625825 Eb0.963022030752082 r0 p11.2666529479903 y-0 TrX-0.31662124018351 TrY-0.234779622084196 TrZ0 Tpy-0 Tpp0 j0 a=0 b=0 c=0 d=0 e=0 g=0 t=0 Va=0 Vb=0 Vc=0 Vd=0 Vx=0 Vy=0  Vm5 n"IMG_6842.JPG"

            # Regex applied to each line
            match = re.search(pattern_image, line)
            if match:
                # Make sure to add \n to display correctly when we write it back
                match = re.search(pattern_imageWidth_imageHeight_imageName, line)
                if match:
                    numGroups = match.groups()
                    width = match.group(1)
                    height = match.group(2)
                    imageFileName = match.group(3)

                    imageInfo = ImageInfo()
                    imageInfo.imageIndex = imageIndex
                    imageIndex += 1
                    imageInfo.imageWidth = int(width)
                    imageInfo.imageHeight = int(height)
                    imageInfo.imageFileName = imageFileName
                    imagesInfo.append(imageInfo)


    wallInfo.overviewImageInfo = overviewImageInfo
    wallInfo.imagesInfo = imagesInfo

    return wallInfo

#####################################

def clampPointToImageSize(overviewImageInfo, projectedPointOrig):
    print( 'BEG clampPointToImageSize' )

    print( 'projectedPointOrig', projectedPointOrig )
    print( 'overviewImageInfo.imageWidth', overviewImageInfo.imageWidth )
    print( 'overviewImageInfo.imageHeight', overviewImageInfo.imageHeight )

    projectedPoint = projectedPointOrig
    projectedPoint[0] = float(projectedPoint[0])
    projectedPoint[1] = float(projectedPoint[1])

    if (projectedPoint[0] < 0) :
        projectedPoint[0] = 0

    if (projectedPoint[0] > overviewImageInfo.imageWidth-1) :
        projectedPoint[0] = overviewImageInfo.imageWidth-1

    if (projectedPoint[1] < 0) :
        projectedPoint[1] = 0

    if (projectedPoint[1] > overviewImageInfo.imageHeight-1) :
        projectedPoint[1] = overviewImageInfo.imageHeight-1

    print( 'projectedPoint0', projectedPoint )

    # truncate to 2 decimals after the dot
    projectedPoint[0] = round(float(projectedPoint[0]), 2)
    projectedPoint[1] = round(float(projectedPoint[1]), 2)

    print( 'projectedPoint1', projectedPoint )

    return projectedPoint


#####################################


def calc_uv_coords(pto_filename, wallInfo):

    overviewImageInfo = wallInfo.overviewImageInfo
    imagesInfo = wallInfo.imagesInfo

    # update points of overviewImageInfo with the imageCoords
    overviewImageInfo.tlPoint.imageCoords.x = 0
    overviewImageInfo.tlPoint.imageCoords.y = 0

    overviewImageInfo.trPoint.imageCoords.x = overviewImageInfo.imageWidth-1
    overviewImageInfo.trPoint.imageCoords.y = overviewImageInfo.originY

    overviewImageInfo.blPoint.imageCoords.x = overviewImageInfo.originX
    overviewImageInfo.blPoint.imageCoords.y = overviewImageInfo.imageHeight-1

    overviewImageInfo.brPoint.imageCoords.x = overviewImageInfo.imageWidth-1
    overviewImageInfo.brPoint.imageCoords.y = overviewImageInfo.imageHeight-1

    overviewImageInfo.centerPoint.imageCoords.x = int(overviewImageInfo.imageWidth/2)
    overviewImageInfo.centerPoint.imageCoords.y = int(overviewImageInfo.imageHeight/2)

    #######################################################
    # update points of imageInfo with the imageCoords
    #######################################################

    imagePoints = ''
    for imageInfo in imagesInfo:
        imageInfo.tlPoint.imageCoords.x = 0
        imageInfo.tlPoint.imageCoords.y = 0
        imagePoints += '%s %s %s\n' % (imageInfo.imageIndex, imageInfo.tlPoint.imageCoords.x, imageInfo.tlPoint.imageCoords.y)

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

    # print( 'imagePoints', imagePoints )

    pipe = subprocess.Popen(['pano_trafo', pto_filename], stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE)

    trafoOut = (pipe.communicate(input
                                 = imagePoints.encode('utf-8'))[0]).decode('utf-8')

    splitImagePoints = imagePoints.splitlines()
    splitTrafoOut = trafoOut.splitlines()

    for inPointIndex, inPointStr in enumerate(splitImagePoints):

        inPointArr = inPointStr.split()
        projectedPointStr = splitTrafoOut[inPointIndex]
        projectedPoint = projectedPointStr.split()
        imageIndex = int(inPointArr[0])

        if ((imageIndex<0) or (imageIndex>=len(imagesInfo))):
            print( 'imageIndex', imageIndex )
            raise AssertionError("imageIndex not in imagesInfo")

        imageInfo = imagesInfo[imageIndex]

        # update points of imageInfo with the uvCoords
        point = Point()
        point.imageCoords.x = int(inPointArr[1])
        point.imageCoords.y = int(inPointArr[2])
        imageCoords = point.imageCoords

        doClamp = True
        # doClamp = False
        if doClamp:
            print( 'projectedPoint', projectedPoint )
            projectedPointClamped = clampPointToImageSize(overviewImageInfo, projectedPoint)
            print( 'projectedPointClamped', projectedPointClamped )
            projectedPoint = projectedPointClamped

            point.uvCoords.x = round(float(projectedPoint[0]), 2)
            point.uvCoords.y = round(float(projectedPoint[1]), 2)
        else :
            # truncate to 2 decimals after the dot
            point.uvCoords.x = round(float(projectedPoint[0]), 2)
            point.uvCoords.y = round(float(projectedPoint[1]), 2)

        point.uvCoordsNormalized.x = round(point.uvCoords.x / overviewImageInfo.imageWidth, 2)

        # flip y to match with threejs y coordinate system
        point.uvCoordsNormalized.y = (1-(round(point.uvCoords.y / overviewImageInfo.imageHeight, 2)))
        print( 'point.uvCoordsNormalized.y', point.uvCoordsNormalized.y )


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
            epsilon = 1E-6
            if (point.uvCoords.x < epsilon) and (point.uvCoords.y < epsilon):
                print( 'point' )
                print( point )
                raise AssertionError("length of center point is 0")

        else:
            raise AssertionError("Invalid imageCoords")

        imagesInfo[imageIndex] = imageInfo

    wallInfo.overviewImageInfo = overviewImageInfo
    wallInfo.imagesInfo = imagesInfo

    return wallInfo

#####################################

# based on example4_draw_line_on_3d_model.js::annotationTest
# using barycentric
def ptInTriangle(point, face):

    x0 = point.uvCoordsNormalized.x
    y0 = point.uvCoordsNormalized.y
    # print( 'x0', x0 )
    # print( 'y0', y0 )

    x1 = face.vertices[0].uvCoordsNormalized.x
    y1 = face.vertices[0].uvCoordsNormalized.y
    # print( 'x1', x1 )
    # print( 'y1', y1 )

    x2 = face.vertices[1].uvCoordsNormalized.x
    y2 = face.vertices[1].uvCoordsNormalized.y
    # print( 'x2', x2 )
    # print( 'y2', y2 )

    x3 = face.vertices[2].uvCoordsNormalized.x
    y3 = face.vertices[2].uvCoordsNormalized.y
    # print( 'x3', x3 )
    # print( 'y3', y3 )

    # print( 'face.vertices', face.vertices )

    b0 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    print( 'b0', b0 )
    if b0 == 0:
        raise AssertionError("denominator b0 is 0")

    b1 = ((x2 - x0) * (y3 - y0) - (x3 - x0) * (y2 - y0)) / b0
    b2 = ((x3 - x0) * (y1 - y0) - (x1 - x0) * (y3 - y0)) / b0
    b3 = ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / b0
    print( 'b1', b1 )
    print( 'b2', b2 )
    print( 'b3', b3 )

    # if (b1 > 0) and (b2 > 0) and (b3 > 0) :
    if (b1 >= 0) and (b2 >= 0) and (b3 >= 0) :
        return [b1, b2, b3]
    else :
        return []


#####################################

# based on example4_draw_line_on_3d_model.js::annotationTest
# using barycentric
def annotationTest(point, face):
    result = ptInTriangle(point, face)
    # print( 'result', result )
    return result

#####################################

# based on example4_draw_line_on_3d_model.js::annotationTest
# using barycentric
def calc_point3d_coords(point, faces):

    found_3d_coords_for_point = False

    for index1, face in enumerate(faces):
        baryData = annotationTest(point, face)
        # print( 'baryData', baryData )
        if len(baryData) > 0:
            p0 = face.vertices[0].worldcoords
            p1 = face.vertices[1].worldcoords
            p2 = face.vertices[2].worldcoords
            # Sum the barycentric coordinates and apply to the vertices to get the coordinate in local space
            p3 = Point3d()
            p3.x = p0.x * baryData[0] + p1.x * baryData[1] + p2.x * baryData[2]
            p3.y = p0.y * baryData[0] + p1.y * baryData[1] + p2.y * baryData[2]
            p3.z = p0.z * baryData[0] + p1.z * baryData[1] + p2.z * baryData[2]
            point.worldcoords = p3
            found_3d_coords_for_point = True
            break;

    if not found_3d_coords_for_point:
        print( 'point', point )
        print( 'found_3d_coords_for_point', found_3d_coords_for_point )
        for index1, face in enumerate(faces):
            baryData = annotationTest(point, face)
            print( 'baryData' )
            print( baryData )
            print( 'len(baryData)', len(baryData) )
            print( 'face' )
            print( face )

        # sys.exit()

    return point

#####################################

def calc_points3d_coords(wallInfo):

    faces = wallInfo.faces
    overviewImageInfo = wallInfo.overviewImageInfo
    imagesInfo = wallInfo.imagesInfo

    #######################################################
    # For each image corner, find a face that it is within
    # Calc the 3d coords of the corner:
    # - calc barycentric parameters, from uv coords
    # - calc 3d coord from barycentric params
    #######################################################

    for index0, imageInfo in enumerate(imagesInfo):
        imageInfo.tlPoint = calc_point3d_coords(imageInfo.tlPoint, faces)
        imageInfo.trPoint = calc_point3d_coords(imageInfo.trPoint, faces)
        imageInfo.blPoint = calc_point3d_coords(imageInfo.blPoint, faces)
        imageInfo.brPoint = calc_point3d_coords(imageInfo.brPoint, faces)
        imageInfo.centerPoint = calc_point3d_coords(imageInfo.centerPoint, faces)


    wallInfo.overviewImageInfo = overviewImageInfo
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

    wallInfo = extract_images_info_from_pto_file(args.pto_filename)

    wallInfo = calc_uv_coords(args.pto_filename, wallInfo)

    # M-x json-pretty-print-buffer
    json_wall_attributes_filename = args.wall_attributes_filename


    (filename_without_extension, filename_suffix) = os.path.splitext(json_wall_attributes_filename)
    print( 'filename_without_extension', filename_without_extension )
    print( 'filename_suffix', filename_suffix )

    pickle_wall_attributes_filename = filename_without_extension + '.pickle'
    print( 'pickle_wall_attributes_filename', pickle_wall_attributes_filename )

    with open(json_wall_attributes_filename, 'w') as outfile:
        json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

    with open(pickle_wall_attributes_filename, 'w') as outfile:
        pickle.dump(wallInfo, outfile)

    print( 'END Main' )
