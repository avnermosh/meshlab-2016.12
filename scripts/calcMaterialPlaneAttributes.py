
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
from imageInfo import WallInfo, ImageInfo, Point, Point2d, MyJsonEncoder
import re
import pickle


#####################################

def parse_3d_model_json_file():

    with open(args.threed_model_json_filename, 'r') as infile:
        threed_model = json.load(infile)

    return( threed_model )

#####################################

def calcFaceAttributes(index1, face_indices, verticeVals, face_uValues, face_vValues):

    numFaceIndicesPerFace = 3
    index2 = index1 * numFaceIndicesPerFace

    faceVertex = Point()
    faceVertexIndex = face_indices[index2]
    print( 'faceVertexIndex', faceVertexIndex )
    print( 'verticeVals[faceVertexIndex]', verticeVals[faceVertexIndex] )
    faceVertex.worldcoords.x = float(verticeVals[faceVertexIndex])
    faceVertex.worldcoords.y = float(verticeVals[faceVertexIndex+1])
    faceVertex.worldcoords.z = float(verticeVals[faceVertexIndex+2])

    faceVertex.uvCoords.x = face_uValues[index2]
    faceVertex.uvCoords.y = face_vValues[index2]

    # faceVertex.imageCoords is filled later on by calcAttributesOf3dModelImages.py

    return faceVertex

#####################################


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Top level arguments", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--threed_model_json_filename",
                        type=str,
                        default="/tmp/tmp1/mainHouse/3543_W18_shimi_mainHouse.json",
                        help="The json filename of the 3d model attributes")

    parser.add_argument("--out_dir",
                        type=str,
                        default="/tmp/tmp1",
                        help="The output directory name for the materials planes attributes")

    args = parser.parse_args()
    print( 'args', args )

    threed_model = parse_3d_model_json_file()
    # print( 'threed_model', threed_model )

    vertices = threed_model['vertices']
    # print( 'vertices', vertices )
    print( 'len(vertices)', len(vertices) )

    verticeVals = vertices[0]['values']
    # print( 'verticeVals', verticeVals )
    print( 'len(verticeVals)', len(verticeVals) )

    connectivity = threed_model['connectivity']
    # print( 'connectivity', connectivity )
    print( 'len(connectivity)', len(connectivity) )

    face_indices = connectivity[0]['indices']
    # print( 'face_indices', face_indices )
    print( 'len(face_indices)', len(face_indices) )

    face_uValues = connectivity[0]['uValues']
    # print( 'face_uValues', face_uValues )
    # print( 'len(face_uValues)', len(face_uValues) )

    face_vValues = connectivity[0]['vValues']
    # print( 'face_vValues', face_vValues )
    # print( 'len(face_vValues)', len(face_vValues) )

    face_materialIndices = connectivity[0]['materialIndices']
    # print( 'face_materialIndices', face_materialIndices )
    print( 'len(face_materialIndices)', len(face_materialIndices) )

    face_materialNames = connectivity[0]['materialNames']
    # print( 'face_materialNames', face_materialNames )
    # print( 'len(face_materialNames)', len(face_materialNames) )

    wallsInfo = {}
    for index1, materialIndex in enumerate(face_materialIndices):
        print( 'materialIndex', materialIndex )

        if (materialIndex != -1):
            wallInfo = WallInfo()
            if (materialIndex not in wallsInfo):
                wallInfo.materialIndex = materialIndex
                wallInfo.materialName = face_materialNames[index1]
            else:
                wallInfo = wallsInfo[materialIndex]

            # fill the point3d, and uvCoord into for the face vertex
            faceVertex = calcFaceAttributes(index1, face_indices, verticeVals, face_uValues, face_vValues)

            # populate the face vertex info (point3d, and uvCoord) into wallInfo.wallImageInfo
            if (faceVertex.uvCoords == Point2d(0,0)):
                wallInfo.wallImageInfo.tlPoint = faceVertex
            elif (faceVertex.uvCoords == Point2d(1,0)):
                wallInfo.wallImageInfo.trPoint = faceVertex
            elif (faceVertex.uvCoords == Point2d(0,1)):
                wallInfo.wallImageInfo.blPoint = faceVertex
            elif (faceVertex.uvCoords == Point2d(1,1)):
                wallInfo.wallImageInfo.brPoint = faceVertex
            else:
                print( 'faceVertex', faceVertex )
                raise AssertionError("Invalid uvCoords")

            print( 'wallInfo', wallInfo )
            wallsInfo[materialIndex] = wallInfo



    # materialInfo === wallInfo
    #
    # For each materialIndex (maps to materialName, e.g. room1/wall1/wall_fused.jpg)
    #  - create file materialName.json, e.g. /tmp/tmp1/wall1_image_attributes.json
    #  - for materialIndex populate point3d, uvCoords, for vertices of materialIndex
    #  - call calcAttributesOf3dModelImages.py to calc attributes of images of the materialIndex

    print( 'END Main' )
