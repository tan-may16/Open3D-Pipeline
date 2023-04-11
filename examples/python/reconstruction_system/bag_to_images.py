import os
import yaml
import rosbag
import cv2
from cv_bridge import CvBridge
import numpy as np
import argparse


def extract_rgb(bag, args):
    
    
    TOPIC = "/camera/color/image_raw"
    DESCRIPTION = ""
    image_topic = bag.read_messages(TOPIC)
    length = bag.get_message_count(TOPIC)
    if args.all:
        args.num_images = length
    print("-" * 80)
    print("Total Color image number: {}, downsampling to {}".format(length, args.num_images))
    saved_name = []
    count = 0
    for k, b in enumerate(image_topic):
        if (count >= args.num_images): break
        if k % (length // args.num_images) == 0 and k < (length // args.num_images) * args.num_images:
            bridge = CvBridge()
            cv_image = bridge.imgmsg_to_cv2(b.message, b.message.encoding)
            scale_percent = args.scale_percent  # percent of original size
            width = int(cv_image.shape[1] * scale_percent / 100)
            height = int(cv_image.shape[0] * scale_percent / 100)
            cv_image = cv2.resize(cv_image, (width, height))
            cv_image.astype(np.uint8)
            
            saved_name.append(str(count) + ".png") # for images.txt
            
            output_path = os.path.join(args.output_path, "color", str(count) + ".png")
            cv2.imwrite(
                output_path,
                cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR))
            count += 1

            print("saved: " + DESCRIPTION + str(count) + ".png")
    return saved_name, height, width


def extract_depth_original(bag, args):
    TOPIC = "/camera/depth/image_rect_raw"
    DESCRIPTION = ""
    image_topic = bag.read_messages(TOPIC)
    length = bag.get_message_count(TOPIC)
    if args.all:
        args.num_images = length
    print("-" * 80)
    print("Total Original Depth image number: {}, downsampling to {}".format(length, args.num_images))
    
    count = 0
    for k, b in enumerate(image_topic):
        if (count >= args.num_images): break
        if k % (length // args.num_images) == 0 and k < (length // args.num_images) * args.num_images:
            
            bridge = CvBridge()
            cv_image = bridge.imgmsg_to_cv2(b.message, b.message.encoding)
            cv_image.astype(np.uint8)

            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(cv_image, alpha=0.03), cv2.COLORMAP_JET)
            cv2.imwrite(
                os.path.join(args.output_path, "depth_original", str(count) + ".png"),
                depth_colormap)
            count += 1

            print("saved: " + DESCRIPTION + str(count) + ".png")

    return


def extract_aligned_depth(bag, args):
    TOPIC = "/camera/aligned_depth_to_color/image_raw"
    DESCRIPTION = ""
    image_topic = bag.read_messages(TOPIC)
    length = bag.get_message_count(TOPIC)
    if args.all:
        args.num_images = length
    print("-" * 80)
    print("Total Depth image number: {}, downsampling to {}".format(length, args.num_images))
    count = 0
    for k, b in enumerate(image_topic):
        if (count >= args.num_images): break
        if k % (length // args.num_images) == 0 and k < (length // args.num_images) * args.num_images:
            bridge = CvBridge()
            cv_image = bridge.imgmsg_to_cv2(b.message, b.message.encoding)
            
            cv2.imwrite(
                os.path.join(args.output_path, "depth", str(count) + ".png"),
                cv_image)
            count += 1
            print("saved: " + DESCRIPTION + str(count) + ".png")

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Read rosbag and export to images and database")

    parser.add_argument(
        "-i", "--rosbag", type=str, help="path to bag file", required=True
    )
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        help="path to extracted RGB and Depth images",
        default = "dataset/"
    )
    parser.add_argument(
        "-n",
        "--num_images",
        type=int,
        help="number of images desired for extraction",
        default = 1,
    )
    parser.add_argument(
        "-s", "--scale_percent", type=int, default=100, help="resolution scale"
    )
    parser.add_argument(
        "--rgb_only", help="only extract rgb to reduce time", action="store_true"
    )
    parser.add_argument(
        "--original_depth", help="extract original depth images", action="store_true"
    )
    parser.add_argument(
        "--all", help="extract all images", action="store_true"
    )

    args = parser.parse_args()
    if not os.path.exists(os.path.join(args.output_path, "color")):
        os.makedirs(os.path.join(args.output_path, "color"))
        
        
    

    bag = rosbag.Bag(args.rosbag)

   
    if args.rgb_only:
        saved_name, h, w = extract_rgb(bag, args)
    else:
        if not os.path.exists(os.path.join(args.output_path, "depth")):
            os.makedirs(os.path.join(args.output_path, "depth"))
        saved_name, h, w = extract_rgb(bag, args)
        extract_aligned_depth(bag, args)
    
    if args.original_depth:
        if not os.path.exists(os.path.join(args.output_path, "depth_original")):
            os.makedirs(os.path.join(args.output_path, "depth_original"))
        extract_depth_original(bag, args)
        

    bag.close()

    print("ROSBAG EXTRACTION PROCESS COMPLETE")
    
