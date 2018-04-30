
#!/usr/bin/python

"""
parse 3543_W18_shimi_mainHouse.json
For each materialIndex (maps to materialName, e.g. room1/wall1/wall_fused.jpg)
 - create file materialName.json, e.g. /tmp/tmp1/wall1_image_attributes.json
 - for materialIndex populate point3d, uvCoords, for vertices of materialIndex
 - call calcAttributesOf3dModelImages.py to calc attributes of images of the materialIndex

usage example:
python ~/avner/meshlab/branches/meshlab-2016.12/scripts/calcMaterialPlaneAttributes.py \
 --3dmodel_json_filename /tmp/tmp1/mainHouse/3543_W18_shimi_mainHouse.json \
 --out_dir /tmp/tmp1/
"""

import argparse
import subprocess
import glob
import tempfile
import os
import sys
import json
from json import JSONEncoder
from imageInfo import WallInfo, ImageInfo, Face, Point, Point2d, MyJsonEncoder
import re
import pickle

import os.path

#####################################

def parse_3d_model_json_file(threed_model_json_filename):

    with open(threed_model_json_filename, 'r') as infile:
        threed_model = json.load(infile)

    return( threed_model )

#####################################

def calcFaceAttributes(index_in_face_materialIndices, face_indices, verticeVals, face_uValues, face_vValues):

    numVerticesPerFace = 3
    numCoordsPerVertex = 3
    faceVertexIndex = index_in_face_materialIndices * numVerticesPerFace

    print( 'index_in_face_materialIndices', index_in_face_materialIndices )

    face = Face()

    if (index_in_face_materialIndices==4):
        print( 'verticeVals', verticeVals )

    face.vertices = []
    for i in range(0, numVerticesPerFace):

        vertexIndex = face_indices[faceVertexIndex] * numCoordsPerVertex

        faceVertex = Point()

        faceVertex.worldcoords.x = float(verticeVals[vertexIndex])
        faceVertex.worldcoords.y = float(verticeVals[vertexIndex+1])
        faceVertex.worldcoords.z = float(verticeVals[vertexIndex+2])

        # faceVertex.uvCoords.x = TBD
        # faceVertex.uvCoords.y = TBD

        faceVertex.uvCoordsNormalized.x = face_uValues[faceVertexIndex]

        # (no need to flip y to match with threejs y coordinate system because face_vValues
        # is already coming from the threejs coordinate system)
        faceVertex.uvCoordsNormalized.y = face_vValues[faceVertexIndex]
        
        # faceVertex.imageCoords = TBD
        # faceVertex.imageCoords is filled later on by calcAttributesOf3dModelImages.py

        if (index_in_face_materialIndices==4) or (index_in_face_materialIndices==5):
            print( 'faceVertexIndex', faceVertexIndex )
            print( 'vertexIndex', vertexIndex )
            print( 'faceVertex.worldcoords.x', faceVertex.worldcoords.x )
            print( 'faceVertex.worldcoords.y', faceVertex.worldcoords.y )
            print( 'faceVertex.worldcoords.z', faceVertex.worldcoords.z )
            print( 'faceVertex.uvCoordsNormalized.x', faceVertex.uvCoordsNormalized.x )
            print( 'faceVertex.uvCoordsNormalized.y', faceVertex.uvCoordsNormalized.y )
            
        face.vertices.append(faceVertex)

        faceVertexIndex += 1

    return face

#####################################

def populateWallsInfo(threed_model_json_filename):

    threed_model = parse_3d_model_json_file(threed_model_json_filename)
    # print( 'threed_model', threed_model )

    vertices = threed_model['vertices']
    # print( 'vertices', vertices )
    # print( 'len(vertices)', len(vertices) )

    verticeVals = vertices[0]['values']
    # print( 'verticeVals', verticeVals )
    # print( 'len(verticeVals)', len(verticeVals) )

    connectivity = threed_model['connectivity']
    # print( 'connectivity', connectivity )
    # print( 'len(connectivity)', len(connectivity) )

    face_indices = connectivity[0]['indices']
    # print( 'face_indices', face_indices )
    # print( 'len(face_indices)', len(face_indices) )

    face_uValues = connectivity[0]['uValues']
    # print( 'face_uValues', face_uValues )
    # print( 'len(face_uValues)', len(face_uValues) )

    face_vValues = connectivity[0]['vValues']
    # print( 'face_vValues', face_vValues )
    # print( 'len(face_vValues)', len(face_vValues) )

    face_materialIndices = connectivity[0]['materialIndices']
    # print( 'face_materialIndices', face_materialIndices )
    # print( 'len(face_materialIndices)', len(face_materialIndices) )

    face_materialNames = connectivity[0]['materialNames']
    # print( 'face_materialNames', face_materialNames )
    # print( 'len(face_materialNames)', len(face_materialNames) )

    wallsInfo = {}
    for index_in_face_materialIndices, materialIndex in enumerate(face_materialIndices):
        # print( 'materialIndex', materialIndex )

        if (materialIndex != -1):
            wallInfo = WallInfo()
            if (materialIndex not in wallsInfo):
                wallInfo.materialIndex = materialIndex
                wallInfo.materialName = face_materialNames[index_in_face_materialIndices]
            else:
                wallInfo = wallsInfo[materialIndex]

            #######################################################
            # Populate the 3 face vertices with point3d, and uvCoord
            #######################################################

            face = calcFaceAttributes(index_in_face_materialIndices, face_indices, verticeVals, face_uValues, face_vValues)
            wallInfo.faces.append(face)

            # if (wallInfo.materialName == 'room1/wall3/wall_fused.jpg'):
            #     print( 'wallInfo.faces2', wallInfo.faces )
            #     # sys.exit()

            for index2, faceVertex in enumerate(face.vertices):

                # map the 3 face vertices into the 4 corner points of overviewImageInfo
                if (faceVertex.uvCoords == Point2d(0,0)):
                    wallInfo.overviewImageInfo.tlPoint = faceVertex
                elif (faceVertex.uvCoords == Point2d(1,0)):
                    wallInfo.overviewImageInfo.trPoint = faceVertex
                elif (faceVertex.uvCoords == Point2d(0,1)):
                    wallInfo.overviewImageInfo.blPoint = faceVertex
                elif (faceVertex.uvCoords == Point2d(1,1)):
                    wallInfo.overviewImageInfo.brPoint = faceVertex
                else:
                    print( 'faceVertex', faceVertex )
                    raise AssertionError("Invalid uvCoords")

            wallsInfo[materialIndex] = wallInfo
            # print( 'wallsInfo[materialIndex].faces', wallsInfo[materialIndex].faces )

    return wallsInfo

#####################################
