
#import sqlite3
#
#import file_structure_constants
#
#conn = sqlite3.connect('/home/mls278/database/nplab_images.db')
#conn.execute('pragma foreign_keys = on')
#cursor = conn.cursor()
#
#confs_json = open(conf_file_path).read()

import json
import sys
import os
import pymaxwell as pm
from glob import glob
import sqlite3

conn = sqlite3.connect('/home/mls278/database/nplab_images.db')
conn.execute('pragma foreign_keys = on')
cursor = conn.cursor()

cursor.execute('''DELETE * FROM Scenes''')
cursor.execute('''DELETE * FROM CameraTargets''')
cursor.execute('''DELETE * FROM Configs''')
cursor.execute('''DELETE * FROM Traces''')
cursor.execute('''DELETE * FROM Frames''')
conn.commit()


def strip_suffix(s, suffix):
	if s.endswith(suffix):
		s = s[:-(len(suffix)+1)]
	return s

def ensure_suffix(s, suffix):
	if not s.endswith(suffix):
		s = s + suffix
	return s

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
		t = (scene_name, 'u', 'u', 'u', 'u', 'u', 'u', 'u', 'u')
		cursor.execute('''INSERT INTO Scenes(scene, SKPLastModified, SKPHash, ThumbLastModified, ThumbHash, MXSLastModified, MXSHash, CTSLastModified, CTSHash)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', t)
		conn.commit()
		t = (scene_name,)
		sceneID = cursor.fetchone('''SELECT sceneID FROM Scenes WHERE scene = ?''', t)[0]
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
			t = (sceneID, camera_id, target_id)
			cursor.execute('''INSERT INTO CameraTargets(sceneID, camera, target)
			VALUES (?, ?, ?)''', t)
			conn.commit()
			pair_dicts += [{'camera': camera_dict[camera_id],
							'target': target_dict[target_id]}]
		ctss[scene_name] = pair_dicts
		# TODO: confirm mxs file exists
"""
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
			trace_conf_scene_dir = trace_conf_dir + scene_name + '/'
			found_trace_files = pm.getFilesFromPath(trace_conf_scene_dir,trace_file_suffix)
			pairs = ctss[scene_name]
			expected_trace_files = []
			for pair in pairs:
				camera_json = pair['camera']
				target_json = pair['target']
				camera_id = camera_json['id']
				target_id = target_json['id']
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
					framerate = trajectory['sample_rate']
					duration = trajectory['duration']
					trace = trajectory['trace']
					frame_index = 0
					# output dir
					mxs_output_scene_trace_dir = mxs_output_scene_dir + trace_file_name + '/'
					for trace_pt in trace:
						"""