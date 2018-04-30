
#!/usr/bin/python

"""
parse 3543_W18_shimi_mainHouse.json
For each materialIndex (maps to materialName, e.g. room1/wall1/wall_fused.jpg)
 - create file materialName.json, e.g. /tmp/tmp1/wall1_image_attributes.json
 - for materialIndex populate point3d, uvCoords, for vertices of materialIndex
 - call calcAttributesOf3dModelImages.py to calc attributes of images of the materialIndex

usage example:
python ~/avner/meshlab/branches/meshlab-2016.12/scripts/calcMaterialPlaneAttributes.py \
 --threed_model_json_filename /tmp/tmp1/mainHouse/3543_W18_shimi_mainHouse.json \
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
from calcAttributesOf3dModelImages import extract_images_info_from_pto_file, calc_uv_coords, calc_points3d_coords
from calcTopologyOf3dModelImages import createTopology
from calcAttributesOf3dModel import calcFaceAttributes, populateWallsInfo
from create_overview_image_and_calc_uv_coords_using_grid import calc_images_coords_normalized, mosaic_images

import os.path

#####################################

def calc_uv_coords_using_hugin(wallInfo, abs_dir):

    #######################################################
    # Extract the following attributes for the following image types:
    # - overviewImageInfo: imageWidth, imageHeight
    # - imageInfo: imageIndex, imageWidth, imageHeight, imageFileName
    #######################################################

    print( 'Extract wall images info' )

    # pto_filename = '/tmp/wall1.pto'
    pto_filename = '%s/%s' % (abs_dir, 'wall.pto')
    # print( 'pto_filename', pto_filename )

    if not os.path.isfile(pto_filename) :
        # continue
        return (False, wallInfo)

    # skip wall.pto for now it does not have a ROI to compute image width/height from
    if pto_filename == '/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall6/wall.pto':
        print( 'Skipping pto_filename: ', pto_filename )
        # continue
        return (False, wallInfo)

    wallInfo = extract_images_info_from_pto_file(wallInfo, pto_filename)

    # if (wallInfo.materialName == 'room1/wall3/wall_fused.jpg'):
    #     print( 'wallInfo', wallInfo )
    #     print( 'wallInfo.faces3', wallInfo.faces )
    #     print( 'wallInfo.materialIndex', wallInfo.materialIndex )
    #     print( 'wallInfo.materialName', wallInfo.materialName )
    #     sys.exit()

    #######################################################
    # Calc uv ccords
    #######################################################
    print( 'Calc uv ccords' )

    wallInfo = calc_uv_coords(pto_filename, wallInfo)

    return (True, wallInfo)
    

#####################################

def calc_uv_coords_using_grid(wallInfo):

    #######################################################
    # Extract the following attributes for the following image types:
    # - overviewImageInfo: imageWidth, imageHeight
    # - imageInfo: imageIndex, imageWidth, imageHeight, imageFileName
    #######################################################

    print( 'Extract wall images info' )

    # wallInfo = extract_images_info_from_pto_file(wallInfo, pto_filename)
    (imagesInfo, canvas_width_in_pixels, canvas_height_in_pixels) = calc_images_coords_normalized()
    
    # TBD
    
    return wallInfo

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

    # FixME this parameter is not active currently
    parser.add_argument("--out_dir",
                        type=str,
                        default="/tmp/tmp1",
                        help="The output directory name for the materials planes attributes")

    args = parser.parse_args()
    # print( 'args', args )
    # sys.exit()


    #######################################################
    # Populate walls info
    #######################################################
    print( 'Populate walls info' )

    wallsInfo = populateWallsInfo(args.threed_model_json_filename)

    for wallInfo in wallsInfo.values():

        print( 'Doing wallInfo.materialName', wallInfo.materialName )

        #######################################################
        # Calculate wall info
        #######################################################

        top_dir = '/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse'
        rel_dir = os.path.dirname(wallInfo.materialName)
        abs_dir = '%s/%s' % (top_dir, rel_dir)
        # print( 'rel_dir', rel_dir )
        
        do_calc_uv_coords_using_hugin = True

        if do_calc_uv_coords_using_hugin:
            print( 'Calculate uv coords using Hugin' )
            (retval, wallInfo) = calc_uv_coords_using_hugin(wallInfo, abs_dir)
            if not retval:
                print( 'Failed to calc wall info. Continue to next wall.' )
                continue
        else:
            print( 'Calculate uv coords using Grid' )
            (retval, wallInfo) = calc_uv_coords_using_grid(wallInfo, abs_dir)
            
        
        #######################################################
        # Save intermediate wall info to pickle file
        #######################################################

        json_wall_attributes_filename = '%s/%s' % (abs_dir, 'wall_image_attributes.json')
        (filename_without_extension, filename_suffix) = os.path.splitext(json_wall_attributes_filename)

        pickle_wall_attributes_filename = '%s/%s' % (abs_dir, 'wall_image_attributes.pickle')

        with open(json_wall_attributes_filename, 'w') as outfile:
            json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

        # print( 'json_wall_attributes_filename', json_wall_attributes_filename )
        # print( 'wallInfo.faces', wallInfo.faces )
        # sys.exit()

        with open(pickle_wall_attributes_filename, 'w') as outfile:
            pickle.dump(wallInfo, outfile)


        #######################################################
        # Calc 3d points
        #######################################################
        print( 'Calc 3d points' )

        # TBD
        wallInfo = calc_points3d_coords(wallInfo)
        # print( 'wallInfo', wallInfo )
        # sys.exit()

        # calc point3d based on barycentric
        # store in wall_image_attributes1.json
        # sys.exit()

        #######################################################
        # Create topology
        #######################################################
        print( 'Create topology' )

        wall_attributes_filename2 = '%s/%s' % (abs_dir, 'wall_image_attributes2.json')

        # with open(pickle_wall_attributes_filename, 'r') as infile:
        #     wallInfo = pickle.load(infile)

        wallInfo = createTopology(wallInfo)

        #######################################################
        # Save wall attributes to file
        #######################################################
        print( 'Save wall attributes to file: ', wall_attributes_filename2 )

        with open(wall_attributes_filename2, 'w') as outfile:
            json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))


    # materialInfo === wallInfo
    #
    # For each materialIndex (maps to materialName, e.g. room1/wall1/wall_fused.jpg)
    #  - create file materialName.json, e.g. /tmp/tmp1/wall1_image_attributes.json
    #  - for materialIndex populate point3d, uvCoords, for vertices of materialIndex
    #  - call calcAttributesOf3dModelImages.py to calc attributes of images of the materialIndex

    print( 'END Main' )
