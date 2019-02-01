import bpy
import bmesh
import numpy as np
import scipy.spatial as spatial
from random import random
from mathutils import Vector, Matrix
import colorsys
import utils


# Convert hsv values to gamma corrected rgb values
# Based on: http://stackoverflow.com/questions/17910543/convert-gamma-rgb-curves-to-rgb-curves-with-no-gamma/
def convert_hsv(hsv):
    return tuple(pow(val, 2.2) for val in colorsys.hsv_to_rgb(*hsv))

def voronoi_landscape(n=50, w=10, h=5):
    bm = bmesh.new()
    
    w = 1
    y = 1
    z = 1
    for x in range(0,10):
        face = bm.faces.new([
            bm.verts.new([x,0,0]),
            bm.verts.new([x+1,0,0]),
            bm.verts.new([x+1,1,0]),
            bm.verts.new([x,1,0])
        ])
        
        bmesh.ops.recalc_face_normals(bm, faces=[face])
        r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
        
        f = r['faces'][0]
        
        bmesh.ops.translate(bm, vec=Vector((0, 0, -np.random.randint(0, 10))), verts=f.verts)
        
    me = bpy.data.meshes.new("VornoiMesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Voronoi", me)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()
        
        #z = np.random.randint(-10,10)
        #bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
        
        #bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    
    #bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 0))

    



if __name__ == '__main__':
    print(__file__)

    # Remove all elements
    utils.removeAll()

    # Create object
    voronoi_landscape()
    
    # Create lamps
    utils.rainbowLights()

    # Create camera and lamp
    target = utils.target((0, 0, 3))
    utils.camera((-8, -12, 11), target, type='ORTHO', ortho_scale=5)
    #utils.lamp((10, -10, 10), target=target, type='SUN')

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Render scene
    utils.renderToFolder('rendering', 'vornoi_landscape', 500, 500)
