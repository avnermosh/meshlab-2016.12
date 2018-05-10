
#!/usr/bin/python

"""
parse 3543_W18_shimi_mainHouse.json
For each materialIndex (maps to materialName, e.g. room1/wall1/wall_fused.jpg)
 - create file materialName.json, e.g. /tmp/tmp1/wall1_image_attributes.json
 - for materialIndex populate point3d, uvCoords, for vertices of materialIndex
 - call calcMaterialPlaneImageAttributesViaHugin.py to calc attributes of images of the materialIndex

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
from calcMaterialPlaneImageAttributesViaHugin import hugin_extract_images_info_from_pto_file, hugin_calc_uv_coords, calc_points3d_coords
from calcMaterialPlaneImageAttributesViaGrid import grid_extract_images_info_from_dir, grid_calc_uv_coords, create_overview_image
from calcPlaneImagesTopology import createTopology
from calc3dModelAttributes import calcFaceAttributes, populateWallsInfo

import os.path

#####################################

def calc_uv_coords_using_hugin(wallInfo, abs_dir):

    #######################################################
    # Extract the following attributes for the following image types:
    # - overviewImageInfo: imageWidth, imageHeight
    # - imageInfo: imageIndex, imageWidth, imageHeight, imageFilename
    #######################################################

    print( '-----------------------------' )
    print( 'Extract wall images info using Hugin' )
    print( '-----------------------------' )

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

    wallInfo = hugin_extract_images_info_from_pto_file(wallInfo, pto_filename)

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

    wallInfo = hugin_calc_uv_coords(pto_filename, wallInfo)

    return (True, wallInfo)


#####################################

def calc_uv_coords_using_grid(wallInfo, plane_dir):

    #######################################################
    # Extract the following attributes for the following image types:
    # - overviewImageInfo: imageWidth, imageHeight
    # - imageInfo: imageIndex, imageWidth, imageHeight, imageFilename
    #######################################################

    print( '-----------------------------' )
    print( 'Extract wall images info using Grid' )
    print( '-----------------------------' )

    # plane_dir = '/home/avner/avner/constructionOverlay/data/2910_w47_shertzer/floor0/wall_1'
    # /home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse
    print( 'plane_dir', plane_dir )

    wallInfo = grid_extract_images_info_from_dir(wallInfo, plane_dir)

    image_layout_filename = os.path.join(plane_dir, 'image_layout.json')
    with open(image_layout_filename, 'r') as infile:
        image_layout = json.load(infile)

    print( 'image_layout', image_layout )

    wallInfo = grid_calc_uv_coords(wallInfo,
                                   image_layout['num_images_in_rows'],
                                   image_layout['overlap_between_rows'],
                                   image_layout['overlap_between_cols'],
                                   image_layout['scan_mode'])

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

    parser.add_argument("--dataset_dir",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse",
                        help="The dataset directory")

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

    print( '-----------------------------' )
    print( 'Populate walls info' )
    print( '-----------------------------' )

    wallsInfo = populateWallsInfo(args.threed_model_json_filename)

    #######################################################
    # Calculate walls info
    #######################################################

    # for wallInfo in wallsInfo.values():
    for index, wallInfo in enumerate(wallsInfo.values()):

        print( 'Doing wallInfo.materialName', wallInfo.materialName )

        print( 'index', index )
        # if index == 1:
        #     print( 'Done Calculate wall info' )
        #     sys.exit()

        #######################################################
        # Calculate wall info
        #######################################################

        print( 'wallInfo', wallInfo )

        # rel_dir = os.path.dirname(wallInfo.materialName)
        # print( 'rel_dir', rel_dir )
        # plane_dir = '%s/%s' % (args.dataset_dir, rel_dir)

        # change directory to dataset dir
        os.chdir( args.dataset_dir )

        # set plane_dir (relative dir)
        plane_dir = os.path.dirname(wallInfo.materialName)

        print( 'plane_dir1', plane_dir )
        # omit the "./" at the beginning of the plane_dir
        plane_dir = re.sub(r"\.\/", '', plane_dir)
        print( 'plane_dir2', plane_dir )

        do_calc_uv_coords_using_hugin = True
        do_calc_uv_coords_using_hugin = False

        if do_calc_uv_coords_using_hugin:
            print( '-----------------------------' )
            print( 'Calculate uv coords using Hugin' )
            print( '-----------------------------' )

            (retval, wallInfo) = calc_uv_coords_using_hugin(wallInfo, plane_dir)
            if not retval:
                print( 'Failed to calc wall info. Continue to next wall.' )
                continue
        else:
            print( '-----------------------------' )
            print( 'Calculate uv coords using Grid' )
            print( '-----------------------------' )

            wallInfo = calc_uv_coords_using_grid(wallInfo, plane_dir)

            print( '-----------------------------' )
            print( 'Create overview image' )
            print( '-----------------------------' )

            create_overview_image(wallInfo)
        
        #######################################################
        # Save intermediate wall info to pickle file
        #######################################################

        json_wall_attributes_filename = '%s/%s' % (plane_dir, 'wall_image_attributes.json')
        (filename_without_extension, filename_suffix) = os.path.splitext(json_wall_attributes_filename)

        pickle_wall_attributes_filename = '%s/%s' % (plane_dir, 'wall_image_attributes.pickle')

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

        print( '-----------------------------' )
        print( 'Calc 3d points' )
        print( '-----------------------------' )

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

        print( '-----------------------------' )
        print( 'Create topology' )
        print( '-----------------------------' )

        wall_attributes_filename2 = '%s/%s' % (plane_dir, 'wall_image_attributes2.json')

        # with open(pickle_wall_attributes_filename, 'r') as infile:
        #     wallInfo = pickle.load(infile)

        # FixME:
        # disable topology for now, due to assertion error (where one of the image centers vectors is a dot)
        # wallInfo = createTopology(wallInfo)

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
    #  - call calcMaterialPlaneImageAttributesViaHugin.py to calc attributes of images of the materialIndex

    print( 'END Main' )
