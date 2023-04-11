# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023 www.open3d.org
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------------

# examples/python/reconstruction_system/run_system.py

import json
import argparse
import time
import datetime
import os, sys
from os.path import isfile

import open3d as o3d

pyexample_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pyexample_path)

from open3d_example import check_folder_structure

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from initialize_config import initialize_config, dataset_loader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconstruction system")
    parser.add_argument("--config",
                        help="path to the config file",
                        default=None)
    parser.add_argument("--default_dataset",
                        help="(optional) default dataset to be used, only if "
                        "config file is not provided. "
                        "Options: [lounge, bedroom, jack_jack]",
                        type=str,
                        default="lounge")
    parser.add_argument("--make",
                        help="Step 1) make fragments from RGBD sequence.",
                        action="store_true")
    parser.add_argument(
        "--register",
        help="Step 2) register all fragments to detect loop closure.",
        action="store_true")
    parser.add_argument("--refine",
                        help="Step 3) refine rough registrations",
                        action="store_true")
    parser.add_argument(
        "--integrate",
        help="Step 4) integrate the whole RGBD sequence to make final mesh.",
        action="store_true")
    parser.add_argument(
        "--slac",
        help="Step 5) (optional) run slac optimization for fragments.",
        action="store_true")
    parser.add_argument(
        "--slac_integrate",
        help="Step 6) (optional) integrate fragments using slac to make final "
        "pointcloud / mesh.",
        action="store_true")
    parser.add_argument("--debug_mode",
                        help="turn on debug mode.",
                        action="store_true")
    parser.add_argument(
        '--device',
        help="(optional) select processing device for slac and slac_integrate. "
        "[example: cpu:0, cuda:0].",
        type=str,
        default='cpu:0')
    parser.add_argument(
        '--max_depth',
        help="(optional) select max depth to process",
        type=int,
        default= -1)
    parser.add_argument(
        '--tsdf_size',
        help="(optional) select voxel size",
        type=float,
        default= -1)
    parser.add_argument(
        "--visualize",
        help="Whether to visualize the pointcloud",
        action="store_true")
    

    args = parser.parse_args()
    if not args.make and \
            not args.register and \
            not args.refine and \
            not args.integrate and \
            not args.slac and \
            not args.slac_integrate:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # load dataset and check folder structure
    if args.config is not None:
        with open(args.config) as json_file:
            config = json.load(json_file)
            initialize_config(config)
            check_folder_structure(config['path_dataset'])
    else:
        # load deafult dataset.
        config = dataset_loader(args.default_dataset)
    if (args.max_depth != -1):
        config["depth_max"] = args.max_depth
    if (args.tsdf_size != -1):
        config["tsdf_cubic_size"] = args.tsdf_size
    
    assert config is not None

    if args.debug_mode:
        config['debug_mode'] = True
    else:
        config['debug_mode'] = False

    config['device'] = args.device

    print("====================================")
    print("Configuration")
    print("====================================")
    for key, val in config.items():
        print("%40s : %s" % (key, str(val)))

    times = [0, 0, 0, 0, 0, 0]
    if args.make:
        start_time = time.time()
        import make_fragments
        make_fragments.run(config)
        times[0] = time.time() - start_time
    if args.register:
        start_time = time.time()
        import register_fragments
        register_fragments.run(config)
        times[1] = time.time() - start_time
    if args.refine:
        start_time = time.time()
        import refine_registration
        refine_registration.run(config)
        times[2] = time.time() - start_time
    if args.integrate:
        start_time = time.time()
        import integrate_scene
        integrate_scene.run(config)
        times[3] = time.time() - start_time
    if args.slac:
        start_time = time.time()
        import slac
        slac.run(config)
        times[4] = time.time() - start_time
    if args.slac_integrate:
        start_time = time.time()
        import slac_integrate
        slac_integrate.run(config)
        times[5] = time.time() - start_time
        
    if (args.integrate and args.visualize):
        
        point_cloud_file = os.path.join(os.path.join(config['path_dataset'],config["folder_scene"]), "integrated.ply")
        pcd = o3d.io.read_point_cloud(point_cloud_file)
        o3d.visualization.draw_geometries([pcd], window_name='Integrated_pointcloud', width = 800, height = 600)
    
    
    if not os.path.exists(os.path.join(config['path_dataset'], "time.txt")):
        f = open(os.path.join(config['path_dataset'], "time.txt"), "x")
    else:
        f = open("time.txt", "w")
    lines = [
        "==================================== \n",
        "Elapsed time (in h:m:s) \n",
        "==================================== \n",
        "- Making fragments    %s  \n" % datetime.timedelta(seconds=times[0]),
        "- Register fragments  %s  \n" % datetime.timedelta(seconds=times[1]),
        "- Refine registration %s  \n" % datetime.timedelta(seconds=times[2]),
        "- Integrate frames    %s  \n" % datetime.timedelta(seconds=times[3]),
        "- Integrate frames    %s  \n" % datetime.timedelta(seconds=times[3]),
        "- SLAC                %s  \n" % datetime.timedelta(seconds=times[4]),
        "- SLAC Integrate      %s  \n" % datetime.timedelta(seconds=times[5]),
        "- Total               %s  \n" % datetime.timedelta(seconds=sum(times))
    ]
    f.writelines(lines)
    f.close()

    print("====================================")
    print("Elapsed time (in h:m:s)")
    print("====================================")
    print("- Making fragments    %s" % datetime.timedelta(seconds=times[0]))
    print("- Register fragments  %s" % datetime.timedelta(seconds=times[1]))
    print("- Refine registration %s" % datetime.timedelta(seconds=times[2]))
    print("- Integrate frames    %s" % datetime.timedelta(seconds=times[3]))
    print("- SLAC                %s" % datetime.timedelta(seconds=times[4]))
    print("- SLAC Integrate      %s" % datetime.timedelta(seconds=times[5]))
    print("- Total               %s" % datetime.timedelta(seconds=sum(times)))
    
    if (not args.integrate and args.visualize and args.make):
        
        point_cloud_file = os.path.join(os.path.join(config['path_dataset'],config["folder_fragment"]), "fragment_000.ply")
        pcd = o3d.io.read_point_cloud(point_cloud_file)
        o3d.visualization.draw_geometries([pcd], window_name='Fragmented_pointclouds', width = 800, height = 600)
        
    
    sys.stdout.flush()
