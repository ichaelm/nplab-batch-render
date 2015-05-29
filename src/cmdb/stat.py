import sys
import sqlite3
from cmdb import files

def main(main_dir):
    
    conn = sqlite3.connect('/home/mls278/database/nplab_render.db', 60)
    conn.execute('pragma foreign_keys = on')
    cursor = conn.cursor()
    
    main_dir = files.ensure_suffix(main_dir, '/')
    
    cursor.execute('''SELECT COUNT(*) FROM Configs''')
    numConfigs = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM Scenes''')
    numScenes = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM CameraTargets''')
    numCTs = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM Traces''')
    numTraces = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM Frames''')
    numFrames = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM Frames WHERE hasFrameMXS != 0''')
    numFramesWithMXS = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM Frames WHERE hasImage != 0''')
    numFramesWithImage = cursor.fetchone()[0]
    
    print(str(numConfigs) + ' configs')
    print(str(numScenes) + ' scenes')
    print(str(numCTs) + ' camera-target pairs')
    print(str(numTraces) + ' traces')
    print(str(numFrames) + ' frames')
    print(str(numFramesWithMXS) + ' frames with MXS')
    print(str(numFramesWithImage) + ' frames with image')

if __name__ == "__main__":
    main(sys.argv[1])