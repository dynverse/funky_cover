import bpy
import numpy as np
import pandas as pd

import json

import funky
import utils

### PREPARING THE DATA ###


### SETTING THE SCENE ###

# Create lamp
target = utils.target((2/3 * w_overall, h_overall/2, d_overall*3.4/4))
lamp = utils.lamp((w_overall + 10, -20, 50), target=target, type='AREA', shadow = True)
lamp.data.distance = 0.02
lamp.data.energy = 0.0001
lamp.scale = [100, 100, 1]

# Choose either camera
# orthographic camera
# target = utils.target((w_overall/2, h_overall/2, d_overall*3.4/4))
# camera = utils.camera((3/4 * w_overall, -30, 50), target = target, type='ORTHO', ortho_scale=w_overall * 1.2)

# perspective camera
target = utils.target((w_overall/2, h_overall/2, d_overall*3.4/4))
camera = utils.camera((3/4 * w_overall, -30, 50), target = target, lens = 20)