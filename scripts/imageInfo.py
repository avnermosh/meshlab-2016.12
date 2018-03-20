#!/usr/bin/python

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

    def __eq__(self, other):
        return ((self.x == other.x) and (self.y == other.y))

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)


#####################################

class Point3d:
    def __init__(self):
	self.x = 0
	self.y = 0
	self.z = 0

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
	self.worldcoords = Point3d()

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
        self.imageWidth = 4752
        self.imageHeight = 3168 
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


#####################################

class WallInfo:
    def __init__(self):
	self.wallImageInfo = ImageInfo()
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

        
