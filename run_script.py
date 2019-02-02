import bpy
import os
import sys

# Specify the script to be executed
scriptFile = "voronoi_landscape.py"

# Get absolute path to current folder
filesDir = os.path.dirname(os.path.abspath(__file__.replace("funky_cover.blend/", "")))

# Get scripts folder and add it to the search path for modules
cwd = filesDir
sys.path.append(cwd)
# Change current working directory to scripts folder
os.chdir(cwd)

# Compile and execute script file
file = os.path.join(cwd, scriptFile)
exec(compile(open(file).read(), scriptFile, 'exec'))
