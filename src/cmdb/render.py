import sys
import sqlite3
import subprocess
import os #remove
import time
import random
from cmdb import files

def main(main_dir):

    conn = sqlite3.connect('/home/mls278/database/nplab_render.db', 60)
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()
    
    main_dir = files.ensure_suffix(main_dir, '/')
    
    try:
        jobID = os.environ['PBS_JOBID'].split('.')[0]
    except:
        try:
            jobID = os.getpid()
        except:
            random.seed(time.time())
            jobID = random.randrange(1000000000)
    
    while True:
        conn.execute('''UPDATE Frames SET lockedBy = ?, lockTime = DATETIME("now") WHERE frameID IN (SELECT frameID FROM Frames WHERE lockedBy IS NULL AND hasFrameMXS != 0 AND hasImage = 0 LIMIT 1)''', (jobID,))
        conn.commit()
        cursor.execute('''SELECT configID, scene, camera, target, trace, frame, frameID FROM Scenes NATURAL JOIN CameraTargets NATURAL JOIN Traces NATURAL JOIN Frames WHERE lockedBy = ?''', (jobID,))
        tuples = cursor.fetchall()
        if not tuples:
            break;
        for t in tuples:
            (conf, scene, camera, target, trace, frame, frameID) = t
            mxs_dir = files.get_scene_mxs_dir(main_dir, scene)
            framemxs_path = files.get_frame_mxs_path(main_dir, conf, scene, camera, target, trace, frame)
            image_path = files.get_image_path(main_dir, conf, scene, camera, target, trace, frame)
            files.ensure_directory_exists(os.path.dirname(image_path))
            subprocess.call(['maxwell', '-nogui', '-node', '-nowait', '-trytoresume',
                             '-mxs:' + framemxs_path, '-res:256x256', '-sl:14', '-mxi:' + framemxs_path[:-4] + '_recover.mxi',
                             '-output:' + image_path, '-dep:' + mxs_dir,
                             '-dep:"/usr/local/maxwell-3.0/materials database/textures"',])
            image_info = files.get_image_info(main_dir, conf, scene, camera, target, trace, frame)
            start = time.time()
            conn.execute('''UPDATE Frames SET hasImage = ?, imageLastModified = ?, imageHash = ?, lockedBy = NULL, lockTime = NULL WHERE frameID = ?''', (image_info.hash != None, image_info.last_modified, image_info.hash, frameID))
            conn.commit()
            print("elapsed: " + str(time.time() - start))
    conn.close()
    print("exited normally")

if __name__ == "__main__":
    main(sys.argv[1])