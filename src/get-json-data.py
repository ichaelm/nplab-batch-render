import json


#constants
conf_file_name = 'conf.json'
cts_dir_name = 'cts'
mxs_dir_name = 'mxs'
trace_dir_name = 'trace'
mxs_output_dir_name = 'mxs_frames'
cts_file_suffix = 'cts.json'
mxs_file_suffix = 'mxs'
trace_file_suffix = 'ss.json'

# main_dir = ensure_suffix(main_dir, '/')
# conf_dir = main_dir
# cts_dir = main_dir + cts_dir_name + '/'
# mxs_dir = main_dir + mxs_dir_name + '/'
# trace_dir = main_dir + trace_dir_name + '/'
# mxs_output_dir = main_dir + mxs_output_dir_name + '/'
# conf_file_path = conf_dir + conf_file_name

def get_confs(main_dir):
    main_dir = ensure_suffix(main_dir, '/')
    conf_dir = main_dir
    conf_file_path = conf_dir + conf_file_name
    confs_json = open(conf_file_path).read()
    confs = json.loads(confs_json)
    return confs

def get_cts_filenames(main_dir):
    cts_dir = main_dir + cts_dir_name + '/'
    cts_files = pm.getFilesFromPath(cts_dir, cts_file_suffix)
    cts_filenames = []
    for cts_file in cts_files:
        cts_filename = strip_suffix(cts_file, cts_file_suffix)
        cts_filenames.append(cts_filename)
    return cts_filenames
