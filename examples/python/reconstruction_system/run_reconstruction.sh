#!/bin/bash

rm -rf /dataset/color
rm -rf /dataset/depth



source /home/tanmay/anaconda3/etc/profile.d/conda.sh
conda activate open3d

echo "Input bag file name:"
read bag_name

echo " "

echo " Adaptive frame selection? (y/n):"
read frame

if [ "$frame" == 'y' ]
then
	python2 bag_to_images.py --rosbag $bag_name --all
	echo " Feature Level? (1/2)"
	read level
	echo " "
	echo " Feature Threshold? (0-1)"
	read threshold
	
	python feature_extractor.py --level $level --threshold $threshold

else
	echo "Number of Images"
	read num
	python2 bag_to_images.py --rosbag $bag_name --num_images $num

fi
echo " "

echo "Enter Max_depth for 3D reconstruction"
read max_depth

echo " "

echo "Enter tsdf_cubic Size (1-6)"
read tsdf

echo " "

echo "Integrate? (y/n):"
read integrate

echo "Visualize? (y/n):"
read visualize


if [ "$integrate" == 'y' ] &&  [ "$visualize" == 'y' ]
then
	python run_system.py --config config/realsense.json --make --register --refine --integrate --visualize --max_depth $max_depth --tsdf_size $tsdf
elif [ "$integrate" == 'y' ] &&  [ "$visualize" == 'n' ]
then
	python run_system.py --config config/realsense.json --make --register --refine --integrate --max_depth $max_depth --tsdf_size $tsdf
elif [ "$integrate" == 'n' ] &&  [ "$visualize" == 'y' ]
then
	python run_system.py --config config/realsense.json --make --visualize --max_depth $max_depth --tsdf_size $tsdf
elif [ "$integrate" == 'n' ] &&  [ "$visualize" == 'n' ]
then
	python run_system.py --config config/realsense.json --make --max_depth $max_depth --tsdf_size $tsdf
else 
	echo "Enter Valid arguments"

fi

