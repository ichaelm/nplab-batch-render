import pymaxwell as pm
import sys
from cmdb import files
import sqlite3
import os

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

    conn = sqlite3.connect('/home/mls278/database/nplab_render.db')
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()
    
    trace_memo = {}
    pmscene_memo = {}
    
    cursor.execute('''SELECT configID, scene, camera, target, trace, frame FROM Scenes NATURAL JOIN CameraTargets NATURAL JOIN Traces NATURAL JOIN Frames WHERE Frames.hasMXS = 0''')
    for conf, scene, camera, target, trace, frame in cursor:
        try:
            pmscene = pmscene_memo[scene]
        except:
            pmscene = pm.Cmaxwell(pm.mwcallback);
            ok = scene.readMXS(files.get_scene_mxs_path(main_dir, scene));
            if ok == 0:
                print("Error reading scene");
                return;
            pmscene_memo[scene] = pmscene
        camera = scene.getActiveCamera();
        _,_,_,focalLength,fStop,_,_ = camera.getStep(0);
        print('focalLength = ' + str(focalLength))
        print('fStop = ' + str(fStop))
        try:
            trace = trace_memo[(conf, scene, camera, target, trace)]
        except:
            trace = files.get_trace(main_dir, conf, scene, camera, target, trace)
            trace_memo[(conf, scene, camera, target, trace)] = trace
        camera_pos_vec = to_vec(inches_to_meters(trace.trajectory[frame]))
        target_pos_vec = to_vec(inches_to_meters(trace.target_pos))
        velocity_vec = to_vec(inches_to_meters(trace.velocity))
        framerate = trace.framerate
        camera_end_vec = camera_pos_vec + (velocity_vec * (1.0/framerate))
        shutter = 0.5 / framerate
        pmcamera = pmscene.addCamera('name', 2, shutter, 0.1, 0.1, 100, 'CIRCULAR', 90, 1, framerate, 1024, 1024, 1)
        camera_up_vec = [0.0, 0.0, 1.0]
        pmcamera.setStep(0,camera_pos_vec,target_pos_vec,camera_up_vec,focalLength,fStop,0); 
        pmcamera.setStep(1,camera_end_vec,target_pos_vec,camera_up_vec,focalLength,fStop,1);
        pmcamera.setActive()
        framemxs_path = files.get_frame_mxs_path(main_dir, conf, scene, camera, target, trace, frame)
        files.ensure_directory_exists(os.path.dirname(framemxs_path))
        ok = scene.writeMXS(framemxs_path);
        if ok == 0:
            print("Error saving frame");
            return;

if __name__ == "__main__":
    main(sys.argv[1])
