import bpy
import os
import sys

%load_ext autoreload
%autoreload 2

# define number of available cpus for rendering
from multiprocessing import cpu_count
cores_idle = 2
cores_available = cpu_count()
cores_enabled = max(1, cores_available - cores_idle)
for scene in bpy.data.scenes:
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = cores_enabled

# define run, to easily run a command inside the console
def run(script):
    import os
    cwd = os.getcwd()
    file = os.path.join(cwd, script)
    exec(compile(open(file).read(), script, 'exec'), globals())

# print current working directory, make sure this is the directory of the python scripts!
print(os.getcwd())
sys.path.append(os.getcwd())

import render