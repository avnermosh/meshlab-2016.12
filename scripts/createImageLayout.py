#!/usr/bin/env python

'''
Usage:

python /tmp/createImageLayout.py \
 --num_images_in_rows_str '3, 2, 3' \
 --out_filename /tmp/tmp1.json
'''

import os
import sys
import argparse
import random
import json
import glob

parser = argparse.ArgumentParser(description='Foo.')

parser.add_argument("--num_images_in_rows_str",
                    type=str,
                    required=True,
                    # default='3, 3, 3',
                    help="num_images_in_rows_str")

parser.add_argument("--overlap_between_rows",
                    type=float,
                    default=0.1,
                    help="overlap_between_rows")

parser.add_argument("--overlap_between_cols",
                    type=float,
                    default=0.1,
                    help="overlap_between_cols")

parser.add_argument("--scan_mode",
                    type=str,
                    default='left_to_right__bottom_to_top_snake',
                    help="scan_mode")

parser.add_argument("--in_dir",
                    type=str,
                    required=True,
                    default='/tmp',
                    help="in_dir")

parser.add_argument("--out_filename",
                    type=str,
                    default='image_layout.json',
                    help="out_filename")

args = parser.parse_args()

image_layout_params = {}
image_layout_params["num_images_in_rows"] = args.num_images_in_rows_str
image_layout_params["overlap_between_rows"] = args.overlap_between_rows
image_layout_params["overlap_between_cols"] = args.overlap_between_cols
image_layout_params["scan_mode"] = args.scan_mode

os.chdir( args.in_dir )
# https://stackoverflow.com/questions/168409/how-do-you-get-a-directory-listing-sorted-by-creation-date-in-python/168435#168435
image_order = filter(os.path.isfile, glob.glob("*.JPG"))
image_order.sort(key=lambda x: os.path.getmtime(x))
# print( 'image_order', image_order )

image_layout_params["image_order"] = image_order


# image_layout_params["out_filename"] = args.out_filename

with open(args.out_filename, 'w') as outfile:
    json.dump(image_layout_params, outfile, indent=4)
