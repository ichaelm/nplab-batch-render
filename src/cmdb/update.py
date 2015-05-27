"""unfinished and ill-conceived"""



import sys
import sqlite3
from cmdb import files

def hash_dict(d):
    f = []
    for k, v in d.iteritems():
        try:
            f.append(hash((k, hash(v))))
        except:
            f.append((k, hash_dict(v)))
    return hash(frozenset(f))

class ConfTuple:
    def __init__(self, numTraces, numFrames, JSONHash):
        self.numTraces = numTraces
        self.numFrames = numFrames
        self.JSONHash = JSONHash
        
class SceneTuple:
    def __init__(self, scene, hasSKP, SKPLastModified, SKPHash, hasThumb, thumbLastModified, thumbHash, hasMXS, MXSLastModified, MXSHash, hasCTS, CTSLastModified, CTSHash):
        self.scene = scene
        self.hasSKP = hasSKP
        self.SKPLastModified = SKPLastModified
        self.SKPHash = SKPHash
        self.hasThumb = hasThumb
        self.thumbLastModified = thumbLastModified
        self.thumbHash = thumbHash
        self.hasMXS = hasMXS
        self.MXSLastModified = MXSLastModified
        self.MXSHash = MXSHash
        self.hasCTS = hasCTS
        self.CTSLastModified = CTSLastModified
        self.CTSHash = CTSHash

class CTSTuple:
    def __init__(self, scene, camera, target):
        self.scene = scene
        self.camera = camera
        self.target = target

class TraceTuple:
    def __init__(self, scene, camera, target, conf, trace, trace_info):
        self.scene = scene
        self.camera = camera
        self.target = target
        self.conf = conf
        self.trace = trace
        self.trace_info = trace_info

def main(main_dir):
    
    conn = sqlite3.connect('/home/mls278/database/nplab_render.db')
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()

    main_dir = files.ensure_suffix(main_dir, '/')
    
    # generate an array of fs confs
    # generate an array of db confs
    # for each fs conf:
        # if mirrored in db confs:
            # remove from db confs
        # if exists but wrong in db confs:
            # fix in db, remove from db confs, add to regen_con
        # if not exists in db confs:
            # add to db, add to regen_confs
    # for each db conf left:
        # add to confs_to_remove
    

    # generate fs_confs
    fs_conf_dicts = files.get_confs(main_dir)
    fs_confs = []
    for i, conf_dict in enumerate(fs_conf_dicts):
        num_directions = conf_dict['direction']['options']['ndirections']
        duration = conf_dict['duration']
        sample_rate = conf_dict['sample_rate']
        num_frames = int(duration * sample_rate)
        fs_confs[i] = ConfTuple(num_directions, num_frames, hash_dict(conf_dict))
    
    # generate fs_scenes
    scenes_with_skp = files.get_scenes_with_skp(main_dir)
    scenes_with_thumb = files.get_scenes_with_thumbs(main_dir)
    scenes_with_mxs = files.get_scenes_with_mxs(main_dir)
    scenes_with_cts = files.get_scenes_with_cts(main_dir)
    scenes = set(scenes_with_skp + scenes_with_thumb + scenes_with_mxs + scenes_with_cts) # all scenes
    fs_scenes = []
    for scene in scenes:
        skp_info = files.get_scene_skp_info(main_dir, scene)
        thumb_info = files.get_scene_thumbs_info(main_dir, scene)
        mxs_info = files.get_scene_mxs_info(main_dir, scene)
        cts_info = files.get_scene_cts_info(main_dir, scene)
        fs_scenes.append(SceneTuple(scene, skp_info.hash != None, skp_info.last_modified, skp_info.hash,
                                           thumb_info.hash != None, thumb_info.last_modified, thumb_info.hash,
                                           mxs_info.hash != None, mxs_info.last_modified, mxs_info.hash,
                                           cts_info.hash != None, cts_info.last_modified, cts_info.hash))

    
    #generate fs_ctss
    fs_ctss = []
    for scene in scenes_with_cts:
        ct_pairs = files.get_scene_camera_target_pairs(main_dir, scene)
        for camera, target in ct_pairs:
            fs_ctss.append(CTSTuple(scene, camera, target))
            
    # generate fs_traces
    fs_traces = []
    for cts in fs_ctss:
        scene = cts.scene
        camera = cts.camera
        target = cts.target
        for confID, conf in enumerate(fs_confs):
            for direction in xrange(conf.num_directions):
                trace_info = files.get_trace_info(main_dir, confID, scene, camera, target, direction)
                fs_traces.append(TraceTuple(scene, camera, target, confID, direction, trace_info))
    
    # update all frames
    for traceID, (ctsID, confID, direction) in enumerated_traces.iteritems():
        conf = confs[confID]
        duration = conf['duration']
        sample_rate = conf['sample_rate']
        num_frames = int(duration * sample_rate)
        cts = enumerated_traces[ctsID]
        (scene, camera, target) = cts
        for frame in xrange(num_frames):
            framemxs_info = files.get_frame_mxs_info(main_dir, confID, scene, camera, target, direction, frame)
            image_info = files.get_image_info(main_dir, confID, scene, camera, target, direction, frame)
            t = (traceID, frame, framemxs_info.hash != None, framemxs_info.last_modified, framemxs_info.hash, image_info.hash != None, image_info.last_modified, image_info.hash)
            cursor.execute('''INSERT INTO Frames(traceID, frame, hasMXS, MXSLastModified, MXSHash, hasImage, imageLastModified, imageHash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', t)
            conn.commit()

if __name__ == "__main__":
    main(sys.argv[1])
