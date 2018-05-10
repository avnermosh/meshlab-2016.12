#!/usr/bin/python

import argparse
import subprocess
import glob
import tempfile
import os
import sys
import json
from json import JSONEncoder
import math

#####################################

class Point2d:
    def __init__(self, x=-1, y=-1):
	self.x = x
	self.y = y

    def __eq__(self, other):
        return ((self.x == other.x) and (self.y == other.y))

    def __str__(self):
        sb = []
        for key in self.__dict__:
            # sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
            sb.append("{key}='{value}'".format(key=key, value=math.ceil(self.__dict__[key]*100)/100))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)


#####################################

class Point3d:
    def __init__(self):
	self.x = 0
	self.y = 0
	self.z = 0

    def __eq__(self, other):
        return ((self.x == other.x) and (self.y == other.y) and (self.z == other.z))

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
	self.uvCoordsNormalized = Point2d()
	self.uvCoordsNormalizedYflipped = Point2d()
	self.worldcoords = Point3d()

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)

        
#####################################

class Face:
    def __init__(self):
	self.vertices = []

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)


#####################################

class NeighborImages:
    def __init__(self):
	self.leftImage = NeighborPoint()
	self.rightImage = NeighborPoint()
	self.topImage = NeighborPoint()
	self.bottomImage = NeighborPoint()

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)



#####################################

class NeighborPoint:
    def __init__(self):
	self.pointIndex = -1
	self.distance = 1E6

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
        self.originX = 0
        self.originY = 0
        self.imageWidth = -1
        self.imageHeight = -1 
	self.imageFilename = 'NA'
        self.tlPoint = Point()
        self.trPoint = Point()
        self.blPoint = Point()
        self.brPoint = Point()
        self.centerPoint = Point()
        self.neighborImages = NeighborImages()

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)

    def grid_calc_corner_points_uvCoordsNormalized_y(self, center_y, top_y, bottom_y):
        self.centerPoint.uvCoordsNormalized.y = center_y
        self.tlPoint.uvCoordsNormalized.y = top_y
        self.trPoint.uvCoordsNormalized.y = self.tlPoint.uvCoordsNormalized.y
        self.blPoint.uvCoordsNormalized.y = bottom_y
        self.brPoint.uvCoordsNormalized.y = self.blPoint.uvCoordsNormalized.y
        self.centerPoint.uvCoordsNormalizedYflipped.y = 1 - center_y
        self.tlPoint.uvCoordsNormalizedYflipped.y = 1 - bottom_y
        self.trPoint.uvCoordsNormalizedYflipped.y = self.tlPoint.uvCoordsNormalizedYflipped.y
        self.blPoint.uvCoordsNormalizedYflipped.y = 1 - top_y
        self.brPoint.uvCoordsNormalizedYflipped.y = self.blPoint.uvCoordsNormalizedYflipped.y
        


    def grid_calc_corner_points_uvCoordsNormalized_x(self, overlap_between_cols, image_width_norm, col_index):
        self.centerPoint.uvCoordsNormalized.x = (col_index * image_width_norm * (1-overlap_between_cols)) + (image_width_norm/2)
        self.tlPoint.uvCoordsNormalized.x = self.centerPoint.uvCoordsNormalized.x - (image_width_norm/2)
        self.trPoint.uvCoordsNormalized.x = self.tlPoint.uvCoordsNormalized.x + image_width_norm
        self.blPoint.uvCoordsNormalized.x = self.tlPoint.uvCoordsNormalized.x
        self.brPoint.uvCoordsNormalized.x = self.blPoint.uvCoordsNormalized.x + image_width_norm

        self.centerPoint.uvCoordsNormalizedYflipped.x = self.centerPoint.uvCoordsNormalized.x
        self.tlPoint.uvCoordsNormalizedYflipped.x = self.tlPoint.uvCoordsNormalized.x
        self.trPoint.uvCoordsNormalizedYflipped.x = self.trPoint.uvCoordsNormalized.x
        self.blPoint.uvCoordsNormalizedYflipped.x = self.blPoint.uvCoordsNormalized.x
        self.brPoint.uvCoordsNormalizedYflipped.x = self.brPoint.uvCoordsNormalized.x

    def grid_calc_corner_points_uvCoordsNormalized(self,
                                                   overlap_between_cols,
                                                   row_index,
                                                   col_index,
                                                   image_width_norm,
                                                   center_y,
                                                   top_y,
                                                   bottom_y,
                                                   imageFilename):

        self.grid_calc_corner_points_uvCoordsNormalized_y(center_y, top_y, bottom_y)
        self.grid_calc_corner_points_uvCoordsNormalized_x(overlap_between_cols, image_width_norm, col_index)

        # sanity check
        if not self.grid_are_points_within_bounds:
            print( 'One or more of the points are out of bounds' )
            sys.exit()

        # print( 'imageFilename1', imageFilename )
        self.imageFilename = imageFilename
        # print( 'self.imageFilename', self.imageFilename )

        
    def is_point_within_bounds(self, imagePoint):
        if (imagePoint.uvCoordsNormalized.x < 0.0) or \
           (imagePoint.uvCoordsNormalized.x > 1.0) or \
           (imagePoint.uvCoordsNormalized.y < 0.0) or \
           (imagePoint.uvCoordsNormalized.y > 1.0):
            return False
        else:
            return True

    def grid_are_points_within_bounds(self):
        if not self.is_point_within_bounds(tlPoint):
            print( 'Invalid point tlPoint', tlPoint )
            return False

        if not self.is_point_within_bounds(trPoint):
            print( 'Invalid point trPoint', trPoint )
            return False

        if not self.is_point_within_bounds(blPoint):
            print( 'Invalid point blPoint', blPoint )
            return False

        if not self.is_point_within_bounds(brPoint):
            print( 'Invalid point brPoint', brPoint )
            return False

        if not self.is_point_within_bounds(centerPoint):
            print( 'Invalid point centerPoint', centerPoint )
            return False

        return True

#####################################

class WallInfo:
    def __init__(self):
        self.materialIndex = -1
        self.materialName = 'NA'
        self.faces = []
	self.overviewImageInfo = ImageInfo()
	self.imagesInfo = []

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

        
