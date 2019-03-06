import bpy
import os
import utils
import subprocess
import shutil

def prepare_test_render():
    scene = bpy.context.scene
    scene.world.light_settings.use_ambient_occlusion = True
    scene.world.light_settings.samples = 1
    scene.cycles.use_transparent_shadows = False
    scene.cycles.samples = 5
    scene.cycles.min_bounces = 0
    scene.cycles.max_bounces = 0
    scene.render.tile_x = 128
    scene.render.tile_y = 128

    resX = 12*100
    resY = 9*100
    resPercentage = 100

    scene.render.resolution_x = resX
    scene.render.resolution_y = resY
    scene.render.resolution_percentage = resPercentage

    return scene

# render functions
def test_render():
    scn = prepare_test_render()

    scn.render.filepath = os.path.join("rendering/test.png")
    bpy.ops.render.opengl(write_still=True, view_context=False)

def test_render_animation():
    scn = prepare_test_render()
    frames_folder = "rendering/frames"
    if os.path.exists(frames_folder):
        shutil.rmtree(frames_folder)
    os.mkdir(frames_folder)

    scn.render.filepath = os.path.join(frames_folder + "/frame")
    bpy.ops.render.opengl(animation=True, view_context=False)

    # mp4
    subprocess.run(["ffmpeg", "-y", "-framerate", "25", "-start_number", str(bpy.context.scene.frame_start), "-i", "rendering/frames/frame%04d.png", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p", "rendering/output.mp4"])
    
    # gif from mp4
    subprocess.run(["ffmpeg", "-y", "-i", "rendering/output.mp4", "-r", "50", "-vf", "scale=512:-1", "rendering/output.gif"])

def render():
    # update scene
    bpy.context.scene.update()
    
    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=30)
    
    # Render scene
    utils.renderToFolder('rendering', 'funky_cover', 8.5*300, 11*300)
