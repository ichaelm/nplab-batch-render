import json
from glob import glob
from datetime import datetime
import hashlib
import os

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

#constants
BLOCKSIZE = 65536
hasher = hashlib.md5()

conf_file_name = 'conf.json'

skp_dir_name = 'skp'
thumbs_dir_name = 'thumbnails'
mxs_dir_name = 'mxs'
cts_dir_name = 'cts'
trace_dir_name = 'trace'
framemxs_dir_name = 'mxs_frames'
image_dir_name = 'images'

cts_file_suffix = '.cts.json'
mxs_file_suffix = '.mxs'
trace_file_suffix = '.ss.json'
skp_file_suffix = '.skp'
image_file_suffix = '.png'

# main_dir = ensure_suffix(main_dir, '/')
# conf_dir = main_dir
# cts_dir = main_dir + cts_dir_name + '/'
# mxs_dir = main_dir + mxs_dir_name + '/'
# trace_dir = main_dir + trace_dir_name + '/'
# mxs_output_dir = main_dir + mxs_output_dir_name + '/'
# conf_file_path = conf_dir + conf_file_name

def strip_suffix(s, suffix):
    if s.endswith(suffix):
        s = s[:-len(suffix)]
    return s

def ensure_suffix(s, suffix):
    if not s.endswith(suffix):
        s = s + suffix
    return s

def get_skp_files(main_dir):
    skp_files = glob(main_dir + skp_dir_name + '/*' + skp_file_suffix)
    return skp_files

def get_thumbs_files(main_dir):
    thumbs_files = glob(main_dir + thumbs_dir_name + '/*' + image_file_suffix)
    return thumbs_files

def get_mxs_scene_dirs(main_dir):
    mxs_dirs = glob(main_dir + mxs_dir_name + '/*/')
    return mxs_dirs

def get_mxs_files(main_dir):
    mxs_dirs = get_mxs_scene_dirs(main_dir)
    mxs_files = [(mxs_dir + os.path.basename(strip_suffix(mxs_dir, '/')) + mxs_file_suffix) for mxs_dir in mxs_dirs]
    return mxs_files

def get_cts_files(main_dir):
    cts_files = glob(main_dir + cts_dir_name + '/*' + cts_file_suffix)
    return cts_files

def get_trace_config_dirs(main_dir):
    pass

def get_trace_files(main_dir):
    trace_files = glob(main_dir + trace_dir_name + '/*' + trace_file_suffix)
    return trace_files
    
def get_framemxs_files(main_dir):
    framemxs_files = glob(main_dir + framemxs_dir_name + '/*' + mxs_file_suffix)
    return framemxs_files
    
def get_image_files(main_dir):
    image_files = glob(main_dir + image_dir_name + '/*' + image_file_suffix)
    return image_files

def get_scene_skp_path(main_dir, scene):
    return main_dir + skp_dir_name + '/' + str(scene) + skp_file_suffix

def get_scene_thumbs_path(main_dir, scene):
    return main_dir + thumbs_dir_name + '/' + str(scene) + image_file_suffix

def get_scene_mxs_path(main_dir, scene):
    return main_dir + mxs_dir_name + '/' + str(scene) + '/' + scene + mxs_file_suffix

def get_scene_cts_path(main_dir, scene):
    return main_dir + cts_dir_name + '/' + str(scene) + cts_file_suffix

def get_file_last_modified(file_path):
    if os.path.isfile(file_path):
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    else:
        return None

def get_file_hash(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            buf = f.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(BLOCKSIZE)
        return hasher.hexdigest()
    else:
        return None

class FileInfo:
    def __init__(self, _last_modified, _hash):
        self.last_modified = _last_modified
        self.hash = _hash
        
def get_file_info(file_path):
    return FileInfo(get_file_last_modified(file_path), get_file_hash(file_path))

def filenames(file_paths, extension):
    return [os.path.basename(os.path.splitext(strip_suffix(file_path, extension))[0]) for file_path in file_paths]

def get_scenes_with_skp(main_dir):
    return filenames(get_skp_files(main_dir), skp_file_suffix)

def get_scenes_with_thumbs(main_dir):
    return filenames(get_thumbs_files(main_dir), image_file_suffix)

def get_scenes_with_mxs(main_dir):
    return filenames(get_mxs_files(main_dir), mxs_file_suffix)

def get_scenes_with_cts(main_dir):
    return filenames(get_cts_files(main_dir), cts_file_suffix)

def get_scene_skp_info(main_dir, scene):
    return get_file_info(get_scene_skp_path(main_dir, scene))

def get_scene_thumbs_info(main_dir, scene):
    return get_file_info(get_scene_thumbs_path(main_dir, scene))

def get_scene_mxs_info(main_dir, scene):
    return get_file_info(get_scene_mxs_path(main_dir, scene))

def get_scene_cts_info(main_dir, scene):
    return get_file_info(get_scene_cts_path(main_dir, scene))

def get_confs(main_dir):
    conf_dir = main_dir
    conf_file_path = conf_dir + conf_file_name
    confs_json = open(conf_file_path).read()
    confs = json.loads(confs_json)
    return confs

def get_scene_camera_target_pairs(main_dir, scene):
    cts_path = get_scene_cts_path(main_dir, scene)
    cts_json = open(cts_path).read()
    cts = json.loads(cts_json)
    pairs = []
    for ct in cts['pairs']:
        pairs.append((ct['camera_id'], ct['target_id']))
    return pairs

def get_trace_path(main_dir, config, scene, camera, target, direction):
    return main_dir + trace_dir_name + '/' + 'config_' + str(config) + '/' + str(scene) + '/' + str(camera) + '_' + str(target) + '_' + str(direction) + '_0' + trace_file_suffix

def get_trace_info(main_dir, config, scene, camera, target, direction):
    return get_file_info(get_trace_path(main_dir, config, scene, camera, target, direction))

def get_frame_mxs_path(main_dir, config, scene, camera, target, direction, frame):
    return main_dir + framemxs_dir_name + '/' + 'config_' + str(config) + '/' + str(scene) + '/' + str(camera) + '_' + str(target) + '_' + str(direction) + '_0' + '_frame_' + str(frame) + mxs_file_suffix

def get_frame_mxs_info(main_dir, config, scene, camera, target, direction, frame):
    return get_file_info(get_frame_mxs_path(main_dir, config, scene, camera, target, direction, frame))

def get_image_path(main_dir, config, scene, camera, target, direction, frame):
    return main_dir + image_dir_name + '/' + 'config_' + str(config) + '/' + str(scene) + '/' + str(camera) + '_' + str(target) + '_' + str(direction) + '_0' + '_frame_' + str(frame) + image_file_suffix

def get_image_info(main_dir, config, scene, camera, target, direction, frame):
    return get_file_info(get_image_path(main_dir, config, scene, camera, target, direction, frame))

def ensure_directory_exists(dirpath):
    dirnames = []
    while (dirpath and (dirpath != '/')):
        (dirpath, dirname) = os.path.split(dirpath)
        if dirname:
            dirnames.append(dirname)
    if dirpath:
        dirnames.append(dirpath)
    dirnames.reverse()
    path = ''
    for dirname in dirnames:
        path = os.path.join(path, dirname)
        if not os.path.isdir(path):
            os.makedirs(path)

def get_scene_cameras(main_dir, scene):
    cts_path = get_scene_cts_path(main_dir, scene)
    cts_json = open(cts_path).read()
    cts = json.loads(cts_json)
    cameras = {}
    for camera in cts['cameras']:
        id = camera['id']
        pos = camera['position']['origin']
        cameras[id] = [pos[0], pos[1], pos[2]]
    return cameras

def get_scene_targets(main_dir, scene):
    cts_path = get_scene_cts_path(main_dir, scene)
    cts_json = open(cts_path).read()
    cts = json.loads(cts_json)
    cameras = {}
    for camera in cts['targets']:
        id = camera['id']
        pos = camera['position']['origin']
        cameras[id] = [pos[0], pos[1], pos[2]]
    return cameras

class TraceStruct:
    pass

def get_trace(main_dir, config, scene, camera, target, direction):
    trace_path = get_trace_path(main_dir, config, scene, camera, target, direction)
    trace_json = open(trace_path).read()
    trace = json.loads(trace_json)
    t = TraceStruct()
    t.target_pos = trace['target']['position']['origin']
    trajectory = trace['camera_trajectory']['trace']
    t.trajectory = [pt['origin'] for pt in trajectory]
    t.velocity = trace['camera_trajectory']['motion_info']['init_velocity']
    t.framerate = trace['camera_trajectory']['sample_rate']
    return t

    
    