#!/bin/bash

# if [ $# -ne 5 ]; then
#     echo " Usage: /tmp/renameSh3dMaterialToWallIndex.sh SRC_DIR SRC_NAME DEST_DIR SECTION_INDEX WALL_INDEX, e.g."
#     echo " /tmp/renameSh3dMaterialToWallIndex.sh \ "
#     echo " ./sh3d/section0/2910_w47_shertzer_section0.6a_reduceTextureIndices.json \ "
#     echo " ./sh3d/section0 \ "
#     echo " 2910_w47_shertzer_section0.1_reduceWallThickness_wall_10_56.jpeg \ "
#     echo " 0 \ "
#     echo " 26"
#     echo
#     exit -1
# fi

# threeDModelFfilename=$1
# srcDir=$2
# srcName=$3
# sectionIndex=$4
# wallIndex=$5


if [ $# -ne 2 ]; then
    echo " Usage: /tmp/renameSh3dMaterialToWallIndex.sh SRC_DIR SRC_NAME DEST_DIR SECTION_INDEX WALL_INDEX, e.g."
    echo " /tmp/renameSh3dMaterialToWallIndex.sh \ "
    echo " 2910_w47_shertzer_section0.1_reduceWallThickness_wall_10_56.jpeg \ "
    echo " 26"
    echo
    exit -1
fi


threeDModelFilename="./sh3d/section0/2910_w47_shertzer_section0.6a_reduceTextureIndices.json"
materialFilename="./sh3d/section0/2910_w47_shertzer_section0.6a_reduceTextureIndices.obj.mtl"
srcDir="./sh3d/section0"
srcName=$1
sectionIndex=0
wallIndex=$2


# ./floor0/wall_26
dstDir=./floor$sectionIndex/wall_$wallIndex

# e.g. ./floor0/wall_26/wall_label.jpg
# dstFullFilename=$dstDir/wall_label.jpg

# e.g. ./floor0/wall_26/flatten_canvas.resized.jpg
dstFullFilename=$dstDir/flatten_canvas.resized.jpg


echo "srcDir $srcDir"
echo "srcName $srcName"
echo "dstDir $dstDir"
echo "dstFullFilename $dstFullFilename"
echo "materialFilename $materialFilename"

mv $srcDir/$srcName $dstFullFilename

ls -l $srcDir/$srcName $dstFullFilename

sed -i.bak "s|$srcName|$dstFullFilename|g" $threeDModelFilename

sed -i.bak "s|$srcName|$dstFullFilename|g" $materialFilename


echo "grep $srcName $threeDModelFilename"
grep $srcName $threeDModelFilename

# grep $dstFullFilename $threeDModelFilename

