#!/usr/bin/env python

#####################################

"""
Calculate attributes of plane images:
- image coords
- uv coords
- create overview image

Example usage:

python ~/avner/meshlab/branches/meshlab-2016.12/scripts/calcMaterialPlaneImageAttributesViaGrid.py \
 --plane_dir /home/avner/avner/constructionOverlay/data/2910_w47_shertzer/floor0/wall_1 \
 --num_images_in_rows '3, 3, 3' \
 --overlap_between_rows 0.1 \
 --overlap_between_cols 0.1

"""

#####################################


import argparse
import subprocess
import tempfile
import os
import sys
import json
from json import JSONEncoder
from imageInfo import WallInfo, ImageInfo, Point, Point2d, Point3d, MyJsonEncoder
import re
import pickle
import math
from PIL import Image

#####################################


# based on extract_images_info_from_pto_file
def grid_extract_images_info_from_dir(wallInfo, plane_dir):
    """
    Extract the following attributes for the following images:
    - imageInfo
      -- imageIndex
      -- imageWidth
      -- imageHeight
      -- imageFileName
    """

    # print( 'BEG grid_extract_images_info_from_dir' )
    # print( 'plane_dir', plane_dir )

    # Get the list of images
    filenames = []
    for file in os.listdir(plane_dir):
        if file.endswith(".JPG"):
            filename = os.path.join(plane_dir, file)
            filenames.append(filename)

    print( 'filenames before:', filenames )

    # Get individual images filenames by order of:
    # - creation time

    # filenames.sort(key=lambda x: os.path.getmtime(x))
    # print( 'filenames after1:', filenames )

    # Get individual images filenames by order of:
    # - image index
    filenames.sort(key=lambda f: int(filter(str.isdigit, str(f))))
    print( 'filenames after2:', filenames )

    # populate imageInfos with multiple imageInfo

    # imageIndex: 0
    # imageWidth: 4752
    # imageHeight: 3168
    # imageFilename: IMG_7548.JPG
    #
    # identify /home/avner/avner/constructionOverlay/data/2910_w47_shertzer/floor0/wall_1/IMG_7548.JPG
    # /home/avner/avner/constructionOverlay/data/2910_w47_shertzer/floor0/wall_1/IMG_7548.JPG JPEG 4752x3168 4752x3168+0+0 8-bit sRGB 6.649MB 0.000u 0:00.009

    imagesInfo = []

    for imageIndex, imageFilename in enumerate(filenames):

        print( 'imageFilename', imageFilename )

        img = Image.open(imageFilename)
        # get the image's width and height in pixels
        width, height = img.size
        print( 'img.size', img.size )

        imageInfo = ImageInfo()
        imageInfo.imageIndex = imageIndex
        imageInfo.imageWidth = int(width)
        imageInfo.imageHeight = int(height)
        imageInfo.imageFilename = imageFilename
        imagesInfo.append(imageInfo)

        # print( 'imageInfo', imageInfo )

    # for image_index, imageInfo in enumerate(imagesInfo):
    #     print( 'imageInfo', imageInfo )

    # wallInfo.overviewImageInfo = overviewImageInfo
    wallInfo.imagesInfo = imagesInfo

    return wallInfo

#####################################

def grid_calc_uv_coords(wallInfo,
                        num_images_in_rows,
                        overlap_between_rows,
                        overlap_between_cols,
                        scan_mode):

    print( 'Beg grid_calc_uv_coords' )
    print( 'scan_mode', scan_mode )

    # use the image width/height of the first image (assuming all images have the same width/height)
    image_width_in_pixels = wallInfo.imagesInfo[0].imageWidth
    image_height_in_pixels = wallInfo.imagesInfo[0].imageHeight

    # https://stackoverflow.com/questions/19334374/python-converting-a-string-of-numbers-into-a-list-of-int
    num_images_in_rows = [int(num_images_in_row) for num_images_in_row in num_images_in_rows.split(',')]
    # print( 'num_images_in_rows', num_images_in_rows )
    # [num_images_in_row for num_images_in_row in num_images_in_rows]

    num_rows = len(num_images_in_rows)
    # print( 'num_rows', num_rows )

    image_height_norm = 1 / ((num_rows * (1 - overlap_between_rows)) + overlap_between_rows)
    # print( 'image_height_norm', image_height_norm )



    #######################################################
    # Calc overviewImageInfo attributes
    #######################################################

    print( '-----------------------------' )
    print( 'Calc overviewImageInfo attributes' )
    print( '-----------------------------' )

    overviewImageInfo = wallInfo.overviewImageInfo

    canvas_width_in_pixels = 0
    num_images_total = 0
    for row_index, num_cols in enumerate(num_images_in_rows):
        num_images_total += num_cols
        image_width_norm = 1 / ((num_cols * (1 - overlap_between_cols)) + overlap_between_cols)
        canvas_width_in_pixels_tmp = (1 / image_width_norm) * image_width_in_pixels
        if canvas_width_in_pixels_tmp > canvas_width_in_pixels:
            canvas_width_in_pixels = int(canvas_width_in_pixels_tmp)

    overviewImageInfo.imageWidth = canvas_width_in_pixels
    overviewImageInfo.imageHeight = int((1 / image_height_norm) * image_height_in_pixels)

    overviewImageInfo.trPoint.imageCoords.x = overviewImageInfo.imageWidth-1
    overviewImageInfo.trPoint.imageCoords.y = overviewImageInfo.originY

    overviewImageInfo.blPoint.imageCoords.x = overviewImageInfo.originX
    overviewImageInfo.blPoint.imageCoords.y = overviewImageInfo.imageHeight-1

    overviewImageInfo.brPoint.imageCoords.x = overviewImageInfo.imageWidth-1
    overviewImageInfo.brPoint.imageCoords.y = overviewImageInfo.imageHeight-1

    overviewImageInfo.centerPoint.imageCoords.x = int(overviewImageInfo.imageWidth/2)
    overviewImageInfo.centerPoint.imageCoords.y = int(overviewImageInfo.imageHeight/2)

    wallInfo.overviewImageInfo = overviewImageInfo

    #######################################################
    # update points of imageInfo with the imageCoords
    #######################################################

    print( '-----------------------------' )
    print( 'update imageInfo points uvCoordsNormalized ' )
    print( '-----------------------------' )

    imagesInfo = wallInfo.imagesInfo

    # print( 'num_images_total', num_images_total )
    # sanity check
    if num_images_total != len(imagesInfo):
        print( 'num_images_total (%s), and num_imagesInfo (%s) must be equal' % (num_images_total, len(imagesInfo)) )
        sys.exit()

    imageFilename_index = 0
    is_pass_even = False
    for row_index, num_cols in enumerate(num_images_in_rows):

        # print( '------' )

        # print( 'is_pass_even', is_pass_even )

        # print( 'num_cols', num_cols )
        image_width_norm = 1 / ((num_cols * (1 - overlap_between_cols)) + overlap_between_cols)
        # print( 'image_width_norm', image_width_norm )


        # print( 'row_index before', row_index )

        if (scan_mode == 'left_to_right__bottom_to_top') or (scan_mode == 'left_to_right__bottom_to_top_snake'):
            # reverse the order of y
            row_index = (num_rows-1) - row_index

        # print( 'row_index after', row_index )

        (center_y, top_y, bottom_y) = grid_calc_corner_points_uvCoordsNormalized_y1(overlap_between_rows, image_height_norm, row_index)

        for col_index in range(num_cols):
            # print( 'col_index before', col_index )

            if (scan_mode == 'left_to_right__bottom_to_top_snake'):
                if (is_pass_even):
                    # reverse the order of x for even rows
                    col_index = (num_cols -1) - col_index

            # print( 'col_index after', col_index )

            # print( 'row, col', row_index, col_index )

            imageFilename = wallInfo.imagesInfo[imageFilename_index].imageFilename
            # print( 'imageFilename_index', imageFilename_index )
            print( 'imageFilename', imageFilename )

            # imageInfo = ImageInfo()

            # imageInfo.grid_calc_corner_points_uvCoordsNormalized(overlap_between_cols,
            wallInfo.imagesInfo[imageFilename_index].grid_calc_corner_points_uvCoordsNormalized(overlap_between_cols,
                                                                 row_index,
                                                                 col_index,
                                                                 image_width_norm,
                                                                 center_y,
                                                                 top_y,
                                                                 bottom_y,
                                                                 imageFilename)
            # print( 'imageInfo', imageInfo )

            # imagesInfo.append(imageInfo)
            # print( 'imagesInfo2', imagesInfo )

            imageFilename_index += 1

        is_pass_even = not is_pass_even

    imagesInfoLength = len(wallInfo.imagesInfo)
    print( 'imagesInfoLength5', imagesInfoLength )

    wallInfo.imagesInfo = imagesInfo

    imagesInfoLength = len(wallInfo.imagesInfo)
    print( 'imagesInfoLength6', imagesInfoLength )

    print( 'End grid_calc_uv_coords' )

    return wallInfo


#####################################

def grid_calc_corner_points_uvCoordsNormalized_y1(overlap_between_rows, image_height_norm, row_index):

    # flip y to match with threejs y coordinate system
    centerPoint_y = 1 - ((row_index * image_height_norm * (1-overlap_between_rows)) + (image_height_norm/2))

    # centerPoint_y = (row_index * image_height_norm * (1-overlap_between_rows)) + (image_height_norm/2)
    
    # print( '(image_height_norm/2)', (image_height_norm/2) )
    # print( 'row_index', row_index )
    # print( 'centerPoint_y', centerPoint_y )
    topImagePoint_y = centerPoint_y - (image_height_norm/2)
    bottomImagePoint_y = topImagePoint_y + image_height_norm

    return (centerPoint_y, topImagePoint_y, bottomImagePoint_y)

#####################################

def create_overview_image(wallInfo):

    print( 'BEG create_overview_image' )

    imagesInfo = wallInfo.imagesInfo
    # use the image width/height of the first image (assuming all images have the same width/height)
    print( 'imagesInfo[0]', imagesInfo[0] )
    image_width_in_pixels = imagesInfo[0].imageWidth
    image_height_in_pixels = imagesInfo[0].imageHeight
    print( 'image_width_in_pixels', image_width_in_pixels )
    print( 'image_height_in_pixels', image_height_in_pixels )
    image_ratio = float(image_width_in_pixels) / image_height_in_pixels
    print( 'image_ratio', image_ratio )

    overview_image_resized_width = int(640)
    overview_image_resized_height = int(overview_image_resized_width / image_ratio)

    # extract the out_dir. Use the image filename of the first image
    plane_dir = os.path.dirname(wallInfo.imagesInfo[0].imageFilename)

    cmd_str1 = 'convert'

    for image_index, imageInfo in enumerate(imagesInfo):
        # print( 'imageInfo', imageInfo )
        print( 'image_index', image_index )
        # print( 'imageInfo.tlPoint', imageInfo.tlPoint )
        offset_x = int(imageInfo.tlPoint.uvCoordsNormalizedYflipped.x * wallInfo.overviewImageInfo.imageWidth)

        # offset_y = int(imageInfo.tlPoint.uvCoordsNormalized.y * wallInfo.overviewImageInfo.imageHeight)
        offset_y = int(imageInfo.tlPoint.uvCoordsNormalizedYflipped.y * wallInfo.overviewImageInfo.imageHeight)
        print( 'offset_y', offset_y )
        print( 'imageInfo.imageFilename', imageInfo.imageFilename )

        width = 0
        height = 0
        doStretchImage = True
        doStretchImage = False
        if doStretchImage:
            width = int((imageInfo.trPoint.uvCoordsNormalized.x - imageInfo.tlPoint.uvCoordsNormalized.x) * wallInfo.overviewImageInfo.imageWidth)
            height = int((imageInfo.blPoint.uvCoordsNormalized.y - imageInfo.tlPoint.uvCoordsNormalized.y) * wallInfo.overviewImageInfo.imageHeight)
            imageFilename2 = '%s.resized' % (imageInfo.imageFilename)
            cmd_str2 = 'convert %s -resize %sx%s! %s' % (imageInfo.imageFilename, width, height, imageFilename2)
            print( 'cmd_str2', cmd_str2 )
            subprocess.call(cmd_str2, shell=True)

        else:
            width = image_width_in_pixels
            height = image_height_in_pixels
            imageFilename2 = imageInfo.imageFilename


        cmd_str1 += ' -page %sx%s+%s+%s %s' % (width, height, offset_x, offset_y, imageFilename2)


    overview_image_filename = os.path.join(plane_dir, 'flatten_canvas.jpg')
    cmd_str1 += ' -compose multiply -mosaic -layers flatten %s' % (overview_image_filename)

    print( 'cmd_str1', cmd_str1 )
    subprocess.call(cmd_str1, shell=True)

    overview_image_filename2 = os.path.join(plane_dir, 'flatten_canvas.resized.jpg')
    cmd_str2 = 'convert %s -resize %sx%s! %s' % (overview_image_filename,
                                                 overview_image_resized_width,
                                                 overview_image_resized_height,
                                                 overview_image_filename2)

    print( 'cmd_str2', cmd_str2 )
    subprocess.call(cmd_str2, shell=True)

#####################################

# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

if __name__ == '__main__':

    print("Beg main1")

    # -----------------------------------------------------------------
    # Parse command line arguments
    # -----------------------------------------------------------------

    parser = argparse.ArgumentParser(description='This script generates an overview  mosaic image from multiple images.'
                                     ' It calculates the uv coords of each image in the overview image')

    parser.add_argument("--plane_dir",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/2910_w47_shertzer/floor0/wall_1",
                        help="The name of the panorama file")

    parser.add_argument("--wall_attributes_filename",
                        type=str,
                        default="/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/wall1/wall_image_attributes.json",
                        help="The name wall-images-attributes file")

    parser.add_argument("--num_images_in_rows",
                        type=str,
                        default='3, 4, 3',
                        help="num_images_in_rows")

    parser.add_argument("--overlap_between_rows",
                        type=float,
                        default=0.0,
                        help="overlap_between_rows")

    parser.add_argument("--overlap_between_cols",
                        type=float,
                        default=0.0,
                        help="overlap_between_cols")

    parser.add_argument("--scan_mode",
                        type=str,
                        default='left_to_right__bottom_to_top_snake',
                        help="scan_mode. Optional values: left_to_right__bottom_to_top,"
                        "left_to_right__bottom_to_top_snake, left_to_right__top_bottom")

    args = parser.parse_args()


    wallInfo = WallInfo()
    wallInfo = grid_extract_images_info_from_dir(wallInfo, args.plane_dir)

    # based on
    # wallInfo = hugin_calc_uv_coords(args.pto_filename, wallInfo)

    wallInfo = grid_calc_uv_coords(
        wallInfo,
        args.num_images_in_rows,
        args.overlap_between_rows,
        args.overlap_between_cols,
        args.scan_mode)


    # print( 'wallInfo.imagesInfo22222222222', wallInfo.imagesInfo )

    create_overview_image(wallInfo)


    # # M-x json-pretty-print-buffer
    # json_wall_attributes_filename = args.wall_attributes_filename


    # (filename_without_extension, filename_suffix) = os.path.splitext(json_wall_attributes_filename)
    # print( 'filename_without_extension', filename_without_extension )
    # print( 'filename_suffix', filename_suffix )

    # pickle_wall_attributes_filename = filename_without_extension + '.pickle'
    # print( 'pickle_wall_attributes_filename', pickle_wall_attributes_filename )

    # with open(json_wall_attributes_filename, 'w') as outfile:
    #     json.dump(wallInfo, outfile, cls=MyJsonEncoder, sort_keys=True, indent=4, separators=(',', ': '))

    # with open(pickle_wall_attributes_filename, 'w') as outfile:
    #     pickle.dump(wallInfo, outfile)


    print( 'END Main' )
