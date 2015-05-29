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

def main(main_dir):
    
    conn = sqlite3.connect('/home/mls278/database/nplab_render.db', 60)
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()
    
    cursor.execute('''DELETE FROM Frames''')
    cursor.execute('''DELETE FROM Traces''')
    cursor.execute('''DELETE FROM CameraTargets''')
    cursor.execute('''DELETE FROM Scenes''')
    cursor.execute('''DELETE FROM Configs''')
    
    conn.commit()

    main_dir = files.ensure_suffix(main_dir, '/')

    # update all confs
    confs = files.get_confs(main_dir)
    for i, conf in enumerate(confs):
        num_directions = conf['direction']['options']['ndirections']
        duration = conf['duration']
        sample_rate = conf['sample_rate']
        num_frames = int(duration * sample_rate)
        t = (i, num_directions, num_frames, hash_dict(conf))
        cursor.execute('''INSERT INTO Configs(configID, numTraces, numFrames, JSONHash) VALUES (?, ?, ?, ?)''', t)
    conn.commit()
    
    # update all scenes
    scenes_with_skp = files.get_scenes_with_skp(main_dir)
    scenes_with_thumb = files.get_scenes_with_thumbs(main_dir)
    scenes_with_mxs = files.get_scenes_with_mxs(main_dir)
    scenes_with_cts = files.get_scenes_with_cts(main_dir)
    scenes = set(scenes_with_skp + scenes_with_thumb + scenes_with_mxs + scenes_with_cts) # all scenes
    scene_ids = {}
    for scene in scenes:
        skp_info = files.get_scene_skp_info(main_dir, scene)
        thumb_info = files.get_scene_thumbs_info(main_dir, scene)
        mxs_info = files.get_scene_mxs_info(main_dir, scene)
        cts_info = files.get_scene_cts_info(main_dir, scene)
        t = (scene, skp_info.hash != None, skp_info.last_modified, skp_info.hash, thumb_info.hash != None, thumb_info.last_modified, thumb_info.hash, mxs_info.hash != None, mxs_info.last_modified, mxs_info.hash, cts_info.hash != None, cts_info.last_modified, cts_info.hash)
        cursor.execute('''INSERT INTO Scenes(scene, hasSKP, SKPLastModified, SKPHash, hasThumb, thumbLastModified, thumbHash, hasMXS, MXSLastModified, MXSHash, hasCTS, CTSLastModified, CTSHash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', t)
        conn.commit()
        t = (scene,)
        cursor.execute('''SELECT sceneID FROM Scenes WHERE scene = ?''', t)
        sceneID = cursor.fetchone()[0]
        scene_ids[scene] = sceneID
    
    # update all cts
    enumerated_ctss = {}
    for scene in scenes_with_cts:
        ct_pairs = files.get_scene_camera_target_pairs(main_dir, scene)
        for camera, target in ct_pairs:
            t = (scene_ids[scene], camera, target)
            cursor.execute('''INSERT INTO CameraTargets(sceneID, camera, target) VALUES (?, ?, ?)''', t)
            conn.commit()
            cursor.execute('''SELECT cameraTargetID FROM CameraTargets WHERE sceneID = ? AND camera = ? AND target = ?''', t)
            ctsID = cursor.fetchone()[0]
            t = (scene, camera, target)
            enumerated_ctss[ctsID] = t
            
    # update all traces
    enumerated_traces = {}
    for ctsID, (scene, camera, target) in enumerated_ctss.iteritems():
        for confID, conf in enumerate(confs):
            for direction in xrange(conf['direction']['options']['ndirections']):
                trace_info = files.get_trace_info(main_dir, confID, scene, camera, target, direction)
                t = (ctsID, confID, direction, trace_info.hash != None, trace_info.last_modified, trace_info.hash)
                cursor.execute('''INSERT INTO Traces(cameraTargetID, configID, trace, hasTrace, TraceLastModified, TraceHash) VALUES (?, ?, ?, ?, ?, ?)''', t)
                conn.commit()
                t = (ctsID, confID, direction)
                cursor.execute('''SELECT traceID FROM Traces WHERE cameraTargetID = ? AND configID = ? AND trace = ?''', t)
                traceID = cursor.fetchone()[0]
                enumerated_traces[traceID] = t
    
    # update all frames
    for traceID, (ctsID, confID, direction) in enumerated_traces.iteritems():
        conf = confs[confID]
        duration = conf['duration']
        sample_rate = conf['sample_rate']
        num_frames = int(duration * sample_rate)
        cts = enumerated_traces[ctsID]
        (scene, camera, target) = cts
        for frame in xrange(num_frames):
            #framemxs_info = files.get_frame_mxs_info(main_dir, confID, scene, camera, target, direction, frame)
            #image_info = files.get_image_info(main_dir, confID, scene, camera, target, direction, frame)
            t = (traceID, frame, 0, None, None, 0, None, None)
            cursor.execute('''INSERT INTO Frames(traceID, frame, hasFrameMXS, FrameMXSLastModified, FrameMXSHash, hasImage, imageLastModified, imageHash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', t)
            conn.commit()

if __name__ == "__main__":
    main(sys.argv[1])
