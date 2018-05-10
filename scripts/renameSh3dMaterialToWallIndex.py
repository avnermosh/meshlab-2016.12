#!/usr/bin/env python

'''
Usage:

python ~/avner/meshlab/branches/meshlab-2016.12/scripts/renameSh3dMaterialToWallIndex.py \
 --wallIndex 19 \
 --srcName 2910_w47_shertzer_section0.1_reduceWallThickness_wall_12_68.jpeg

'''

import os
import sys
import argparse
import random
import json
import re
import subprocess

parser = argparse.ArgumentParser(description='Foo.')


parser.add_argument("--threeDModelFfilename",
                    type=str,
                    default='./sh3d/section0/2910_w47_shertzer_section0.6a_reduceTextureIndices.json',
                    help="threeDModelFfilename")

parser.add_argument("--srcDir",
                    type=str,
                    default='./sh3d/section0',
                    help="srcDir")

parser.add_argument("--srcName",
                    type=str,
                    required=True,
                    help="srcName")

parser.add_argument("--sectionIndex",
                    type=int,
                    default=0,
                    help="sectionIndex")

parser.add_argument("--wallIndex",
                    type=int,
                    required=True,
                    help="wallIndex")

args = parser.parse_args()

dstDir = './floor%s/wall_%s' % (args.sectionIndex, args.wallIndex)

# ./floor0/wall_26/wall_label.jpg
dstFullFilename = '%s/wall_label.jpg' % (dstDir)
print( 'dstFullFilename', dstFullFilename )

srcFullFilename = '%s/%s' % (args.srcDir, args.srcName)
print( 'srcFullFilename', srcFullFilename )

# os.rename(srcFullFilename, dstFullFilename)

# cmd_str1 = 'sed -i.bak "s|args.srcName|dstFullFilename|g" args.threeDModelFfilename'
# print( 'cmd_str1', cmd_str1 )
# # subprocess.call(cmd_str1, shell=True)

out_file = open(args.threeDModelFfilename, "w")
sub = subprocess.call(['sed', 's|args.srcName|dstFullFilename|g', args.threeDModelFfilename], stdout=out_file )



# grep $srcName $threeDModelFfilename
line = re.findall(r'args.srcName', args.threeDModelFfilename)
print( 'line', line )

