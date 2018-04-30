#!/usr/bin/env python

#####################################
# Example usage:
#
# python ~/avner/meshlab/branches/meshlab-2016.12/scripts/create_overview_image_and_calc_uv_coords_using_grid.py \
#  --num_images_in_rows '3, 4, 1' \
#  --overlap_between_rows 0.1 \
#  --overlap_between_cols 0.1  \
#  --image_names 'foo1.jpg, foo2.jpg, foo3.jpg, foo4.jpg, foo5.jpg, foo6.jpg, foo7.jpg, foo8.jpg'
#
#####################################


import argparse
import math
import sys
import subprocess

#####################################

class Point2d:
    def __init__(self):
	self.x = -1
	self.y = -1

    def __str__(self):
        sb = []
        for key in self.__dict__:
            # sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
            sb.append("{key}='{value}'".format(key=key, value=math.ceil(self.__dict__[key]*100)/100))

        return ', '.join(sb)

    # print("{0:.2f}".format(a))

    def __repr__(self):
        return str(self)

#####################################

class ImageInfo:
    def __init__(self):
	self.topLeftImagePoint = Point2d()
	self.topRightImagePoint = Point2d()
	self.bottomLeftImagePoint = Point2d()
	self.bottomRightImagePoint = Point2d()
	self.centerImagePoint = Point2d()
        self.image_name = 'NA'

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)

    def __repr__(self):
        return str(self)

    def calc_corner_points_y(self, center_y, top_y, bottom_y):
        self.centerImagePoint.y = center_y
        self.topLeftImagePoint.y = top_y
        self.topRightImagePoint.y = self.topLeftImagePoint.y
        self.bottomLeftImagePoint.y = bottom_y
        self.bottomRightImagePoint.y = self.bottomLeftImagePoint.y


    def calc_corner_points_x(self, overlap_between_cols, image_width_norm, col_index):
        self.centerImagePoint.x = (col_index * image_width_norm * (1-overlap_between_cols)) + (image_width_norm/2)
        self.topLeftImagePoint.x = self.centerImagePoint.x - (image_width_norm/2)
        self.topRightImagePoint.x = self.topLeftImagePoint.x + image_width_norm
        self.bottomLeftImagePoint.x = self.topLeftImagePoint.x
        self.bottomRightImagePoint.x = self.bottomLeftImagePoint.x + image_width_norm

    def calc_image_coords_normalized(self,
                                     overlap_between_cols,
                                     row_index,
                                     col_index,
                                     image_width_norm,
                                     center_y,
                                     top_y,
                                     bottom_y,
                                     image_name):

        self.calc_corner_points_y(center_y, top_y, bottom_y)
        self.calc_corner_points_x(overlap_between_cols, image_width_norm, col_index)

        # sanity check
        if not self.are_points_within_bounds:
            print( 'One or more of the points are out of bounds' )
            sys.exit()

        # print( 'image_name1', image_name )
        self.image_name = image_name
        # print( 'self.image_name', self.image_name )


    def are_points_within_bounds(self):
        if not is_point_within_bounds(topLeftImagePoint):
            print( 'Invalid point topLeftImagePoint', topLeftImagePoint )
            return False

        if not is_point_within_bounds(topRightImagePoint):
            print( 'Invalid point topRightImagePoint', topRightImagePoint )
            return False

        if not is_point_within_bounds(bottomLeftImagePoint):
            print( 'Invalid point bottomLeftImagePoint', bottomLeftImagePoint )
            return False

        if not is_point_within_bounds(bottomRightImagePoint):
            print( 'Invalid point bottomRightImagePoint', bottomRightImagePoint )
            return False

        if not is_point_within_bounds(centerImagePoint):
            print( 'Invalid point centerImagePoint', centerImagePoint )
            return False

        return True



#####################################


def calc_corner_points_y1(overlap_between_rows, image_height_norm, row_index):
    centerImagePoint_y = (row_index * image_height_norm * (1-overlap_between_rows)) + (image_height_norm/2)
    topImagePoint_y = centerImagePoint_y - (image_height_norm/2)
    bottomImagePoint_y = topImagePoint_y + image_height_norm

    return (centerImagePoint_y, topImagePoint_y, bottomImagePoint_y)

def is_point_within_bounds(imagePoint):
    if (imagePoint.x < 0.0) or (imagePoint.x > 1.0) or (imagePoint.y < 0.0) or (imagePoint.y > 1.0):
        return False
    else:
        return True



def mosaic_images(image_width_in_pixels,
                  image_height_in_pixels,
                  imagesInfo,
                  canvas_width_in_pixels,
                  canvas_height_in_pixels):
    print( 'BEG mosaic_images' )

    cmd_str1 = 'convert'

    for image_index, imageInfo in enumerate(imagesInfo):
        print( 'imageInfo', imageInfo )

        offset_x = int(imageInfo.topLeftImagePoint.x * canvas_width_in_pixels)
        offset_y = int(imageInfo.topLeftImagePoint.y * canvas_height_in_pixels)

        width = 0
        height = 0
        doStretchImage = True
        # doStretchImage = False
        if doStretchImage:
            width = int((imageInfo.topRightImagePoint.x - imageInfo.topLeftImagePoint.x) * canvas_width_in_pixels)
            height = int((imageInfo.bottomLeftImagePoint.y - imageInfo.topLeftImagePoint.y) * canvas_height_in_pixels)
            image_name2 = '%s.resized' % (imageInfo.image_name)
            cmd_str2 = 'convert %s -resize %sx%s! %s' % (imageInfo.image_name, width, height, image_name2)
            print( 'cmd_str2', cmd_str2 )
            subprocess.call(cmd_str2, shell=True)
            
        else:
            width = image_width_in_pixels
            height = image_height_in_pixels
            image_name2 = imageInfo.image_name


        cmd_str1 += ' -page %sx%s+%s+%s %s' % (width, height, offset_x, offset_y, image_name2)


    cmd_str1 += ' -compose multiply -mosaic -layers flatten flatten_canvas.jpg'
    print( 'cmd_str1', cmd_str1 )
    subprocess.call(cmd_str1, shell=True)




def calc_images_coords_normalized(num_images_in_rows,
                                  image_names,
                                  overlap_between_rows,
                                  image_height_in_pixels,
                                  overlap_between_cols,
                                  image_width_in_pixels,
                                  scan_mode):

    # https://stackoverflow.com/questions/19334374/python-converting-a-string-of-numbers-into-a-list-of-int
    num_images_in_rows = [int(num_images_in_row) for num_images_in_row in num_images_in_rows.split(',')]
    print( 'num_images_in_rows', num_images_in_rows )
    # [num_images_in_row for num_images_in_row in num_images_in_rows]

    image_names = [image_name for image_name in image_names.split(',')]
    print( 'image_names', image_names )
    num_image_names = len(image_names)
    print( 'num_image_names', num_image_names )

    num_rows = len(num_images_in_rows)
    print( 'num_rows', num_rows )

    image_height_norm = 1 / ((num_rows * (1 - overlap_between_rows)) + overlap_between_rows)
    print( 'image_height_norm', image_height_norm )

    canvas_width_in_pixels = 0
    canvas_height_in_pixels = int((1 / image_height_norm) * image_height_in_pixels)

    num_images_total = 0
    for row_index, num_cols in enumerate(num_images_in_rows):
        num_images_total += num_cols
        image_width_norm = 1 / ((num_cols * (1 - overlap_between_cols)) + overlap_between_cols)
        canvas_width_in_pixels_tmp = (1 / image_width_norm) * image_width_in_pixels
        if canvas_width_in_pixels_tmp > canvas_width_in_pixels:
            canvas_width_in_pixels = int(canvas_width_in_pixels_tmp)

    print( 'num_images_total', num_images_total )
    # sanity check
    if num_images_total != num_image_names:
        print( 'num_images_total (%s), and num_image_names (%s) must be equal' % (num_images_total, num_image_names) )
        sys.exit()

    imagesInfo = []

    image_name_index = 0
    is_pass_even = False
    for row_index, num_cols in enumerate(num_images_in_rows):

        print( '------' )

        # print( 'is_pass_even', is_pass_even )

        # print( 'num_cols', num_cols )
        image_width_norm = 1 / ((num_cols * (1 - overlap_between_cols)) + overlap_between_cols)
        # print( 'image_width_norm', image_width_norm )


        print( 'row_index before', row_index )

        if (scan_mode == 'left_to_right__bottom_to_top') or (scan_mode == 'left_to_right__bottom_to_top_snake'):
            # reverse the order of y
            row_index = (num_rows-1) - row_index

        # print( 'row_index after', row_index )


        (center_y, top_y, bottom_y) = calc_corner_points_y1(overlap_between_rows, image_height_norm, row_index)

        for col_index in range(num_cols):
            # print( 'col_index before', col_index )

            if (scan_mode == 'left_to_right__bottom_to_top_snake'):
                if (is_pass_even):
                    # reverse the order of x for even rows
                    col_index = num_rows - col_index

            # print( 'col_index after', col_index )

            print( 'row, col', row_index, col_index )

            image_name = image_names[image_name_index]
            # print( 'image_name_index', image_name_index )
            # print( 'image_name', image_name )

            imageInfo = ImageInfo()
            imageInfo.calc_image_coords_normalized(overlap_between_cols,
                                                   row_index,
                                                   col_index,
                                                   image_width_norm,
                                                   center_y,
                                                   top_y,
                                                   bottom_y,
                                                   image_name)
            print( 'imageInfo', imageInfo )

            imagesInfo.append(imageInfo)
            print( 'imagesInfo2', imagesInfo )

            image_name_index += 1

        is_pass_even = not is_pass_even

    return (imagesInfo, canvas_width_in_pixels, canvas_height_in_pixels)


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# Parse command line arguments
# -----------------------------------------------------------------

parser = argparse.ArgumentParser(description='This script generates an overview  mosaic image from multiple images.'
                                 ' It calculates the uv coords of each image in the overview image')

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

parser.add_argument("--image_names",
                    type=str,
                    default='foo1.jpg, foo2.jpg',
                    help="image_names")

parser.add_argument("--image_width_in_pixels",
                    type=int,
                    default=640,
                    help="image_width_in_pixels")

parser.add_argument("--image_height_in_pixels",
                    type=int,
                    default=480,
                    help="image_height_in_pixels")

args = parser.parse_args()

# -----------------------------------------------------------------
# Beg main
# -----------------------------------------------------------------

print("Beg main1")

(imagesInfo, canvas_width_in_pixels, canvas_height_in_pixels) = calc_images_coords_normalized(
    args.num_images_in_rows,
    args.image_names,
    args.overlap_between_rows,
    args.image_height_in_pixels,
    args.overlap_between_cols,
    args.image_width_in_pixels,
    args.scan_mode)

print( 'imagesInfo', imagesInfo )
print( 'canvas_width_in_pixels, canvas_height_in_pixels', canvas_width_in_pixels, canvas_height_in_pixels )


mosaic_images(args.image_width_in_pixels,
              args.image_height_in_pixels,
              imagesInfo,
              canvas_width_in_pixels,
              canvas_height_in_pixels)
