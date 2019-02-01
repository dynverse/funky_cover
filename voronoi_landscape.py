import bpy
import bmesh
import numpy as np
import scipy.spatial as spatial
from random import random
from mathutils import Vector, Matrix
import colorsys
import utils

import json

palettes = json.load(open("data/palettes.json"))

def hex_to_rgb(hex):
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2 ,4))

palettes = {
    name:[hex_to_rgb(hex) for hex in palette]
    for name, palette in palettes.items()
}


# Convert hsv values to gamma corrected rgb values
# Based on: http://stackoverflow.com/questions/17910543/convert-gamma-rgb-curves-to-rgb-curves-with-no-gamma/
def convert_hsv(hsv):
    return tuple(pow(val, 2.2) for val in colorsys.hsv_to_rgb(*hsv))

def face_rect(bm, x, z, w = 1):
    face = bm.faces.new([
        bm.verts.new([x - w * z / 2 + 0.5, 0.5 - w * z / 2,0]),
        bm.verts.new([x + w * z / 2 + 0.5, 0.5 - w * z / 2,0]),
        bm.verts.new([x + w * z / 2 + 0.5, 0.5 + w * z / 2,0]),
        bm.verts.new([x - w * z / 2 + 0.5, 0.5 + w * z / 2,0])
    ])
    return face

def face_circle(bm, x, z, r = 0.5):
    face = bm.faces.new([
        bm.verts.new([x + np.cos(theta) * r * z + r, 0 + np.sin(theta) * r * z + r, 0])
        for theta in np.arange(0, np.pi * 2, 0.05)
    ])
    return face

def bars(y = 1, colors = palettes["benchmark"], geom = face_rect):
    bm = bmesh.new()
    
    top_faces = []
    
    data = [np.random.random() for i in range(20)]
    
    # create meshes
    w = 1
    h = 10
    for x, datum in enumerate(data):
        # ground face
        face = geom(bm, x, datum)
        
        # extrude
        bmesh.ops.recalc_face_normals(bm, faces=[face])
        r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
        f = r['faces'][0]
        bmesh.ops.translate(bm, vec=Vector((0, 0, datum*h)), verts=f.verts)
        
        top_faces.append(f)

    # Assign material index to each bar
    for face, datum in zip(top_faces, data):
        idx = np.int(np.floor(len(colors) * datum**2))
        print(idx)
        face.material_index = idx
        for edge in face.edges:
            for f in edge.link_faces:
                f.material_index = idx
    
    # create floor
    floor = bm.faces.new([
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([len(data)+0.5, 0, 0]),
        bm.verts.new([len(data)+0.5, 1, 0]),
        bm.verts.new([-0.5, 1, 0])
    ])
    carpet = bm.faces.new([
        bm.verts.new([-0.5, 0, -100]),
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([-0.5, 1, 0]),
        bm.verts.new([-0.5, 1, -100])
    ])
    
    # create object
    me = bpy.data.meshes.new("VornoiMesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Voronoi", me)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()
    
    # move obj
    obj.location = obj.location + Vector((0, y, 0))

    # Create and assign materials to object
    for color in colors:
        mat = bpy.data.materials.new('Material')
        mat.diffuse_color = color
        mat.diffuse_intensity = 0.9
        obj.data.materials.append(mat)

def reset():
    for material in bpy.data.materials:
        material.user_clear()
        bpy.data.materials.remove(material)

if __name__ == '__main__':
    print(__file__)

    # Remove all elements
    utils.removeAll()
    reset()

    # Create object
    y = 0
    for i in range(4):
        y += 1
        bars(y, geom = face_circle)
        
    y += 1
    for i in range(3):
        y += 1
        bars(y, colors = palettes["stability"], geom = face_rect)
        
    y += 1
    for i in range(4):
        y += 1
        bars(y, colors = palettes["qc"], geom = face_rect)
        
    y += 1
    for i in range(5):
        y += 1
        bars(y, colors = palettes["scaling"], geom = face_circle)
    
    # Create lamps
    #utils.rainbowLights()
    
    # Create camera and lamp
    target = utils.target((5, 8, 5))
    utils.camera((-8, -12, 30), target, type='ORTHO', ortho_scale=20)
    utils.lamp((10, -10, 10), target=target, type='SUN')

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Render scene
    import os
    print(os.getcwd())
    utils.renderToFolder('rendering', 'vornoi_landscape', 500, 500)
