import sqlite3

import file_structure_constants

conn = sqlite3.connect('/home/mls278/database/nplab_images.db')
conn.execute('pragma foreign_keys = on')
cursor = conn.cursor()

confs_json = open(conf_file_path).read()
