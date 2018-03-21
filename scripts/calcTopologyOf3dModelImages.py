
#!/usr/bin/env python

# https://stackoverflow.com/questions/31735499/calculate-angle-clockwise-between-two-points

from math import acos
from math import sqrt
from math import pi

import argparse
import random
import json
import itertools
from imageInfo import ImageInfo, Point, Point2d, MyJsonEncoder, NeighborPoint
import pickle
import os
import sys


def distance(v,w):
    return sqrt((v[0]-w[0])**2+(v[1]-w[0])**2)

def length(v):
    return sqrt(v[0]**2+v[1]**2)

def dot_product(v,w):
    return v[0]*w[0]+v[1]*w[1]

def determinant(v,w):
   return v[0]*w[1]-v[1]*w[0]

def inner_angle(v,w):
    d1 = dot_product(v,w)
    cosx = dot_product(v,w)/(length(v)*length(w))
    rad=acos(cosx) # in radians
    val = rad*180/pi
    
    return rad*180/pi # returns degrees


def angle_clockwise(A, B):
    inner=inner_angle(A,B)
    det = determinant(A,B)
    if det<0: #this is a property of the det. If the det < 0 then B is clockwise of A
        return inner
    else: # if the det > 0 then A is immediately clockwise of B
        return 360-inner


# def computePoints(x, y, imageWidth, imageHeight):

#     centerPoint = Point()
#     centerPoint.imageCoords.x = x
#     centerPoint.imageCoords.y = y
#     centerPoint.uvCoords.x = float(centerPoint.imageCoords.x) / imageWidth
#     centerPoint.uvCoords.y = float(centerPoint.imageCoords.y) / imageHeight

#     tlPoint = Point()
#     tlPoint.imageCoords.x = 0
#     tlPoint.imageCoords.y = 0
#     tlPoint.uvCoords.x = float(0) / imageWidth
#     tlPoint.uvCoords.y = float(0) / imageHeight

#     trPoint = Point()
#     trPoint.imageCoords.x = imageWidth
#     trPoint.imageCoords.y = 0
#     trPoint.uvCoords.x = float(trPoint.imageCoords.x) / imageWidth
#     trPoint.uvCoords.y = float(trPoint.imageCoords.y) / imageHeight

#     brPoint = Point()
#     brPoint.imageCoords.x = imageWidth
#     brPoint.imageCoords.y = imageHeight
#     brPoint.uvCoords.x = float(brPoint.imageCoords.x) / imageWidth
#     brPoint.uvCoords.y = float(brPoint.imageCoords.y) / imageHeight

#     blPoint = Point()
#     blPoint.imageCoords.x = 0
#     blPoint.imageCoords.y = imageHeight
#     blPoint.uvCoords.x = float(blPoint.imageCoords.x) / imageWidth
#     blPoint.uvCoords.y = float(blPoint.imageCoords.y) / imageHeight



#     return (centerPoint, tlPoint, trPoint, brPoint, blPoint)

# -----------------------------------------------------------------
# createTopology
# -----------------------------------------------------------------

def createTopology():

    with open(args.in_wall_attributes_filename, 'r') as infile:
        wallInfo = pickle.load(infile)

    wallImageInfo = wallInfo.wallImageInfo
    imagesInfo = wallInfo.imagesInfo


    # https://stackoverflow.com/questions/27150990/python-itertools-combinations-how-to-obtain-the-indices-of-the-combined-numbers
    indexPairs = list((i,j) for ((i,_),(j,_)) in itertools.combinations(enumerate(imagesInfo), 2))
    for indexPair in indexPairs:
        imageIndex0 = imagesInfo[indexPair[0]].imageIndex
        imageIndex1 = imagesInfo[indexPair[1]].imageIndex

        pointA = [None]*2
        pointA[0] = imagesInfo[indexPair[0]].centerPoint.uvCoordsNormalized.x - imagesInfo[indexPair[1]].centerPoint.uvCoordsNormalized.x
        pointA[1] = imagesInfo[indexPair[0]].centerPoint.uvCoordsNormalized.y - imagesInfo[indexPair[1]].centerPoint.uvCoordsNormalized.y

        pointB = [None]*2
        pointB[0] = 0
        pointB[1] = 1

        angleInDeg = angle_clockwise(pointA, pointB)

        distance1 = distance(pointA, pointB)

        point1 = NeighborPoint()
        point1.pointIndex = imagesInfo[indexPair[0]].imageIndex
        # sanity check
        if (indexPair[0] != imagesInfo[indexPair[0]].imageIndex) :
            print( 'indexPair[0]', indexPair[0] )
            print( 'imagesInfo[indexPair[0]].imageIndex', imagesInfo[indexPair[0]].imageIndex )
            raise AssertionError("indexPair[0] not equal to imagesInfo[indexPair[0]].imageIndex")
        point1.distance = distance1

        point2 = NeighborPoint()
        point2.pointIndex = imagesInfo[indexPair[1]].imageIndex
        if (indexPair[1] != imagesInfo[indexPair[1]].imageIndex) :
            print( 'indexPair[1]', indexPair[1] )
            print( 'imagesInfo[indexPair[1]].imageIndex', imagesInfo[indexPair[1]].imageIndex )
            raise AssertionError("indexPair[1] not equal to imagesInfo[indexPair[1]].imageIndex")
        point2.distance = distance1


        if (angleInDeg>45 and angleInDeg<=135) and (distance1 < imagesInfo[indexPair[0]].neighborImages.rightImage.distance):
            imagesInfo[indexPair[0]].neighborImages.rightImage = point2
            if (distance1 < imagesInfo[indexPair[1]].neighborImages.leftImage.distance):
                imagesInfo[indexPair[1]].neighborImages.leftImage = point1

        elif angleInDeg>135 and angleInDeg<=225 and (distance1 < imagesInfo[indexPair[0]].neighborImages.bottomImage.distance):
            imagesInfo[indexPair[0]].neighborImages.bottomImage = point2
            if (distance1 < imagesInfo[indexPair[1]].neighborImages.topImage.distance):
                imagesInfo[indexPair[1]].neighborImages.topImage = point1

        elif angleInDeg>225 and angleInDeg<=315 and (distance1 < imagesInfo[indexPair[0]].neighborImages.leftImage.distance):
            imagesInfo[indexPair[0]].neighborImages.leftImage = point2
            if (distance1 < imagesInfo[indexPair[1]].neighborImages.rightImage.distance):
                imagesInfo[indexPair[1]].neighborImages.rightImage = point1

        elif ((angleInDeg>0 and angleInDeg<=45) or (angleInDeg>315 and angleInDeg<=360)) and (distance1 < imagesInfo[indexPair[0]].neighborImages.topImage.distance):
            imagesInfo[indexPair[0]].neighborImages.topImage = point2
            if (distance1 < imagesInfo[indexPair[1]].neighborImages.bottomImage.distance):
                imagesInfo[indexPair[1]].neighborImages.bottomImage = point1


    wallInfo.imagesInfo = imagesInfo

    with open(args.out_wall_attributes_filename, 'w') as outfile:
        json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

    return


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# Parse command line arguments
# -----------------------------------------------------------------

parser = argparse.ArgumentParser(description='Caculate topology of wall images.')

parser.add_argument("--in_wall_attributes_filename",
                    type=str,
                    default='/tmp/points2d.pickle',
                    help="Input wall attributes file name")

parser.add_argument("--out_wall_attributes_filename",
                    type=str,
                    default='/tmp/wall_attributes_filename.json',
                    help="Output wall attributes file name")

args = parser.parse_args()

# -----------------------------------------------------------------
# Beg main
# -----------------------------------------------------------------

print("Beg main")

createTopology()
