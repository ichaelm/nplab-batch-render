import json
from glob import glob
from datetime import datetime
import hashlib
 
BLOCKSIZE = 65536
hasher = hashlib.md5()

#constants
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

def get_confs(main_dir):
    conf_dir = main_dir
    conf_file_path = conf_dir + conf_file_name
    confs_json = open(conf_file_path).read()
    confs = json.loads(confs_json)
    return confs

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
	mxs_files = [(mxs_dir + os.path.basename(os.path.strip_suffix(mxs_dir, '/')) + mxs_suffix) for mxs_dir in mxs_dirs]
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

def get_file_last_modified(file_path):
	return datetime.fromtimestamp(os.path.getmtime(file_path))

def get_file_hash(file_path):
	with open(file_path, 'rb') as file:
		buf = file.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = file.read(BLOCKSIZE)
	return hasher.hexdigest()

def filenames(file_paths):
	for file_path in file_paths:
		yield os.path.splitext(os.path.basename(file_path))[0]

def generate_skp_file_path


	
	