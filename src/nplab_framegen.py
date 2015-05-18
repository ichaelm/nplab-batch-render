import json
import pymaxwell as pm
from pprint import pprint
import sys
import os
import shutil
from glob import glob

# /
# /conf.json
# /mxs/
# /mxs/<scene>/
# /mxs/<scene>/<scene>.mxs
# /cts/
# /cts/<scene>.cts.json
# /trace
# /trace/config_<config_index>/
# /trace/config_<config_index>/<scene>/
# /trace/config_<config_index>/<scene>/<camera_id>_<target_id>_<dir_index>_<speed_index>.ss.json

# confs =
# [
#   { 
#     "motion_type"   : "linear",
#     "direction"     : {
#                         "direction_specifier" : "regular_directions_on_plane", 
#                          "options"            : {
#                                                   "plane": "xz",
#                                                   "ndirections": 8
#                                                 }    
#                       },
#     "speed"         : 1.5,
#     "duration"      : 1  ,
#     "sample_rate"   : 120          
#   }
#   ...
# ]

# trace =
# {
#   "camera_trajectory" : {
#     "motion_info" : {
#       "motion_type" : "linear"
#       "acceleration" : 0
#       "init_velocity" : [x,y,z]
#       "init_position" {xyz origin}
#     },
#     "sample_rate" : 120,
#     "trace" : [
#       {
#         "zaxis"
#         "origin"
#         "xaxis"
#         "yaxis"
#       }
#     ],
#     "duration" : 1
#   },
#   "camera" : {
#     "id"
#     "position" : {
#       "zaxis"
#       "origin"
#       "xaxis"
#       "yaxis"
#     }
#   }
#   "target" : {
#     "id"
#     "position" : {
#       "zaxis"
#       "origin"
#       "xaxis"
#       "yaxis"
#     }
#   }
# }

meters_per_inch = 0.0254

def strip_suffix(s, suffix):
    if s.endswith(suffix):
        s = s[:-(len(suffix)+1)]
    return s

def ensure_suffix(s, suffix):
    if not s.endswith(suffix):
        s = s + suffix
    return s

def to_vec(pt):
    return pm.Cvector(pt[0], pt[2], -pt[1])

def inches_to_meters(pt):
    return [meters_per_inch * x for x in pt]

def main(main_dir):

    # constants
    conf_file_name = 'conf.json'
    cts_dir_name = 'cts'
    mxs_dir_name = 'mxs'
    trace_dir_name = 'trace'
    mxs_output_dir_name = 'mxs_frames'
    cts_file_suffix = 'cts.json'
    mxs_file_suffix = 'mxs'
    trace_file_suffix = 'ss.json'

    main_dir = ensure_suffix(main_dir, '/')
    conf_dir = main_dir
    cts_dir = main_dir + cts_dir_name + '/'
    mxs_dir = main_dir + mxs_dir_name + '/'
    trace_dir = main_dir + trace_dir_name + '/'
    mxs_output_dir = main_dir + mxs_output_dir_name + '/'
    conf_file_path = conf_dir + conf_file_name

    # make output dir
    os.mkdir(mxs_output_dir)

    # confs
    confs_json = open(conf_file_path).read()
    confs = json.loads(confs_json)

    cts_files = pm.getFilesFromPath(cts_dir,cts_file_suffix)

    scene_names = []
    ctss = {}

    for cts_file in cts_files:
        scene_name = strip_suffix(cts_file, cts_file_suffix)
        scene_names += [scene_name]
        cts_file_path = cts_dir + cts_file
        cts_json = open(cts_file_path).read()
        cts = json.loads(cts_json)
        cameras = cts['cameras']
        targets = cts['targets']
        pairs = cts['pairs']
        pair_dicts = [] # [ { "camera":<>, "target":<> } ...]
        camera_dict = {}
        target_dict = {}
        for camera in cameras:
            camera_id = camera['id']
            camera_dict[camera_id] = camera
        for target in targets:
            target_id = target['id']
            target_dict[target_id] = target
        for pair in pairs:
            camera_id = pair['camera_id']
            target_id = pair['target_id']
            pair_dicts += [{'camera': camera_dict[camera_id],
                            'target': target_dict[target_id]}]
        ctss[scene_name] = pair_dicts
        # TODO: confirm mxs file exists

    # make output dirs
    for scene_name in scene_names:
        mxs_output_scene_dir = mxs_output_dir + scene_name + '/'
        os.mkdir(mxs_output_scene_dir)

    for conf_index in xrange(len(confs)):
        conf = confs[conf_index]
        num_directions = conf['direction']['options']['ndirections']
        speed = conf['speed']
        duration = conf['duration']
        sample_rate = conf['sample_rate']
        trace_conf_dir = trace_dir + 'config_' + str(conf_index) + '/'
        for scene_name in scene_names:
            mxs_file = scene_name + '.' + mxs_file_suffix
            mxs_scene_dir = mxs_dir + scene_name + '/'
            mxs_path = mxs_scene_dir + mxs_file
            mxs_output_scene_dir = mxs_output_dir + scene_name + '/'
            scene = pm.Cmaxwell(pm.mwcallback);
            ok = scene.readMXS(mxs_path);
            if ok == 0:
                    print("Error reading scene");
                    return 0;
            camera = scene.getActiveCamera();
            _,_,_,focalLength,fStop,_,_ = camera.getStep(0);
            trace_conf_scene_dir = trace_conf_dir + scene_name + '/'
            found_trace_files = pm.getFilesFromPath(trace_conf_scene_dir,trace_file_suffix)
            pairs = ctss[scene_name]
            expected_trace_files = []
            for pair in pairs:
                camera_json = pair['camera']
                target_json = pair['target']
                camera_id = camera_json['id']
                target_id = target_json['id']
                target_pos = target_json['position']['origin']
                target_pos_vec = to_vec(inches_to_meters(target_pos))
                for direction_index in xrange(num_directions):
                    trace_file_name = (str(camera_id) + '_' +
                                       str(target_id) + '_' +
                                       str(direction_index) + '_' +
                                       str(0)) # TODO: does not parse speeds yet
                    trace_file = trace_file_name + '.' + trace_file_suffix
                    expected_trace_files += [trace_file]
                    # TODO: compare found vs expected files
                    trace_file_path = trace_conf_scene_dir + trace_file
                    trace_json = open(trace_file_path).read()
                    trace = json.loads(trace_json)
                    trajectory = trace['camera_trajectory']
                    motion_info = trajectory['motion_info']
                    velocity = motion_info['init_velocity']
                    velocity_vec = to_vec(inches_to_meters(velocity))
                    framerate = trajectory['sample_rate']
                    duration = trajectory['duration']
                    trace = trajectory['trace']
                    frame_index = 0
                    # output dir
                    mxs_output_scene_trace_dir = mxs_output_scene_dir + trace_file_name + '/'
                    shutil.copytree(mxs_scene_dir, mxs_output_scene_trace_dir)
                    for f in glob(mxs_output_scene_trace_dir + '*.' + mxs_file_suffix):
                        os.remove(f)
                    for trace_pt in trace:
                        camera_pos = trace_pt['origin']
                        camera_up = trace_pt['zaxis']
                        camera_pos_vec = to_vec(inches_to_meters(camera_pos))
                        camera_end_vec = camera_pos_vec + (velocity_vec * (1/framerate))
                        camera_up_vec = to_vec(camera_up)
                        fps = 120
                        shutter = 1.0/240
                        camera = scene.addCamera('name', 2, shutter, 0.1, 0.1, 100, 'CIRCULAR', 90, 1, fps, 1024, 1024, 1)
                        camera.setStep(0,camera_pos_vec,target_pos_vec,camera_up_vec,focalLength,fStop,0); 
                        camera.setStep(1,camera_end_vec,target_pos_vec,camera_up_vec,focalLength,fStop,1);
                        camera.setActive()
                        new_mxs_file_name = scene_name + '_' + trace_file_name + '_frame_' + str(frame_index)
                        new_mxs_file = new_mxs_file_name + '.' + mxs_file_suffix
                        new_mxs_path = mxs_output_scene_trace_dir + new_mxs_file
                        print(new_mxs_path)
                        ok = scene.writeMXS(new_mxs_path);
                        if ok == 0:
                                print("Error saving frame");
                                return 0;
                        frame_index += 1
            scene.freeScene()
                    
    """
    json_path = 'C:\\Users\\Michael\\Downloads\\exp20150417\\exp20150417\\trace\\config_0\\cityhall\\1400271165_1400271415_5_0.ss.json'
    mxs_path = 'C:\Users\Michael\Downloads\exp20150417\exp20150417\mxs\cityhall\cityhall.mxs'
    new_mxs_path = 'C:\Users\Michael\Downloads\exp20150417\exp20150417\mxs\cityhall\new_cityhall.mxs'

    #pprint(data);
    
    camera_pos = data['camera']['position']['origin']
    trajectory = []
    for i in range(0,12):
        trajectory += [data['camera_trajectory']['trace'][i]['origin']]

    scene = pm.Cmaxwell(pm.mwcallback);
    ok = scene.readMXS(mxs_path);

    if ok == 0:
            print("Error reading scene");
            return 0;

    # Read active camera from scene
    camera = scene.getActiveCamera();

    position,focalPoint,up,focalLength,fStop,stepTime,x = camera.getStep(0);
    current = camera.getStep(0);
    print(current);

    camera_vec = pm.Cvector(camera_pos[0]*0.0254, camera_pos[1]*0.0254, camera_pos[2]*0.0254);
    target_vec = pm.Cvector(54, 2, -17.6);
    camera.setStep(0,camera_vec,target_vec,up,focalLength,fStop,0);

    # Write a new frame to disk
    ok = scene.writeMXS(mxs_path);

    if ok == 0:
            print("Error saving frame");
            return 0;


    print(camera_pos)
    """

if __name__ == "__main__":
    main(sys.argv[1])
