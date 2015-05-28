import sys
import sqlite3
import subprocess
from cmdb import files

def main(main_dir):

    conn = sqlite3.connect('/home/mls278/database/nplab_render.db')
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT configID, scene, camera, target, trace, frame FROM Scenes NATURAL JOIN CameraTargets NATURAL JOIN Traces NATURAL JOIN Frames WHERE Frames.hasImage = 0''')
    for conf, scene, camera, target, trace, frame in cursor.fetchall():
        mxs_dir = files.get_scene_mxs_dir(main_dir, scene)
        framemxs_path = files.get_frame_mxs_path(main_dir, conf, scene, camera, target, trace, frame)
        image_path = files.get_image_path(main_dir, conf, scene, camera, target, trace, frame)
        subprocess.call(['maxwell', '-nogui', '-node', '-nowait', '-trytoresume',
                         '-mxs:' + framemxs_path, '-res:256x256', '-sl:14', '-mxi:' + framemxs_path[:-4] + '_recover.mxi',
                         '-output:' + image_path, '-dep:' + mxs_dir,
                         '-dep:"/usr/local/maxwell-3.0/materials database/textures"',])
    
if __name__ == "__main__":
    main(sys.argv[1])