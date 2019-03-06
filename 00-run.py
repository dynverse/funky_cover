from mathutils import Vector

import animation
import objects
import utils
import render

# reset scene
utils.reset()

# determine grey horizon color
bpy.data.worlds["World"].horizon_color = [0.04, 0.04, 0.04]

# create some common objects
scene = bpy.context.scene

camera_rotation_n_frames = 100

 # ─── TITLE ─────────────────────────────────────────────────────────────────────

print("STAGE: title")

stage_title = bpy.data.objects.new("stage_title", None)
stage_title.rotation_euler = Vector((0,0,np.pi/2))
stage_title.location = Vector((-20, 0, 0))
scene.objects.link(stage_title)

stage_title["start"] = 0

# add camera and initially look at title stage
camera = utils.camera((0, 0, 0), lens = 20)
utils.look_at(camera, stage_title)
camera.keyframe_insert("rotation_euler", frame = 0)
camera.keyframe_insert("location", frame = 0)
camera.data.keyframe_insert("lens", frame = 0)

run("01-title.py")

if "end" not in stage_title: stage_title["end"] = stage_title["start"]
camera.keyframe_insert("rotation_euler", frame = stage_title["end"])

# ─── EMBEDDINGS ─────────────────────────────────────────────────────────────────

print("STAGE: embeddings")

# create stage
stage_embeddings = bpy.data.objects.new("stage_title", None)
stage_embeddings.rotation_euler = Vector((0,0,0))
stage_embeddings.location = Vector((0, 25, 0))
scene.objects.link(stage_embeddings)
scale = 5
stage_embeddings.scale = Vector((scale, scale, scale))

# move camera
stage_embeddings["start"] = stage_title["end"] + camera_rotation_n_frames
utils.look_at(camera, stage_embeddings)
camera.keyframe_insert("rotation_euler", frame = stage_embeddings["start"])

# add stage
run("02-embeddings.py")

if "end" not in stage_embeddings: stage_embeddings["end"] = stage_embeddings["start"]
camera.keyframe_insert("rotation_euler", frame = stage_embeddings["end"])

# ─── FUNKY HEATMAP ──────────────────────────────────────────────────────────────

print("STAGE: funky heatmap")

# create stage
stage_funky = bpy.data.objects.new("stage_title", None)
stage_funky.rotation_euler = Vector((0,0,-np.pi/2))
stage_funky.location = Vector((100, 0, 0))
scene.objects.link(stage_funky)

# move camera
stage_funky["start"] = stage_embeddings["end"] + camera_rotation_n_frames
utils.look_at(camera, stage_funky)
camera.keyframe_insert("rotation_euler", frame = stage_funky["start"])

# add stage
run("03-funky.py")

camera.keyframe_insert("rotation_euler", frame = stage_funky["end"])

# ─── RENDER ─────────────────────────────────────────────────────────────────────

scene.frame_start = stage_title["start"]
scene.frame_end = stage_funky["end"]

render.test_render()
render.test_render_animation()
