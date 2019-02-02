import bpy
import bmesh
import numpy as np
import pandas as pd
from random import random
from mathutils import Vector, Matrix
import colorsys
import utils

import json

# load in dynbenchmark data
columns_info = pd.read_csv("data/column_info.csv")
columns_groups = pd.read_csv("data/column_groups.csv")

data = pd.read_csv("data/data.csv")

# define palettes
palettes = json.load(open("data/palettes.json"))

def hex_to_rgb(hex):
    h = hex.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2 ,4))

palettes = {
    name:[hex_to_rgb(hex) for hex in palette]
    for name, palette in palettes.items()
}

# define different geoms
def extrude_upwards(bm, face, extrusion):
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    f = r['faces'][0]
    bmesh.ops.translate(bm, vec=Vector((0, 0, extrusion)), verts=f.verts)
    
    return f

def geom_funkyrect(bm, x, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([x - w * datum / 2 + 0.5, 0.5 - w * datum / 2,0]),
        bm.verts.new([x + w * datum / 2 + 0.5, 0.5 - w * datum / 2,0]),
        bm.verts.new([x + w * datum / 2 + 0.5, 0.5 + w * datum / 2,0]),
        bm.verts.new([x - w * datum / 2 + 0.5, 0.5 + w * datum / 2,0])
    ])
    
    face = extrude_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_rect(bm, x, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([x, 0, 0]),
        bm.verts.new([x + 1, 0, 0]),
        bm.verts.new([x + 1, 1,0]),
        bm.verts.new([x, 1,0])
    ])
    
    face = extrude_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_circle(bm, x, datum, h = 10, r = 0.5):
    face = bm.faces.new([
        bm.verts.new([x + np.cos(theta) * r * datum + r, 0 + np.sin(theta) * r * datum + r, 0])
        for theta in np.arange(0, np.pi * 2, 0.05)
    ])
    
    face = extrude_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_bar(bm, x, datum, h = 10, w = 4):
    face = bm.faces.new([
        bm.verts.new([x, 0, 0]),
        bm.verts.new([x + 1, 0, 0]),
        bm.verts.new([x + 1, datum * w, 0]),
        bm.verts.new([x, datum * w, 0])
    ])
        
    face = extrude_upwards(bm, face, datum * h)
    
    return (face, w)

geoms = {
    "funkyrect": geom_funkyrect,
    "rect": geom_rect,
    "circle": geom_circle,
    "bar": geom_bar
}

# draw a column
def draw_column(data, y = 1, colors = palettes["benchmark"], geom = geom_rect):
    bm = bmesh.new()
    
    top_faces = []
    
    # create meshes
    for x, datum in enumerate(data):
        if not np.isnan(datum):
            # ground face
            face, width = geom(bm, x, datum)
            
            # extrude
            top_faces.append(face)
        else:
            top_faces.append("")

    # Assign material index to each bar
    for face, datum in zip(top_faces, data):
        if face != "":
            idx = np.int(np.floor((len(colors)-1) * datum**2))
            print(idx)
            face.material_index = idx
            for edge in face.edges:
                for f in edge.link_faces:
                    f.material_index = idx
    
    # create floor
    floor = bm.faces.new([
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([len(data)+0.5, 0, 0]),
        bm.verts.new([len(data)+0.5, width, 0]),
        bm.verts.new([-0.5, width, 0])
    ])
    carpet = bm.faces.new([
        bm.verts.new([-0.5, 0, -100]),
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([-0.5, width, 0]),
        bm.verts.new([-0.5, width, -100])
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
        
    return width

def reset():
    # remove objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # remove materials
    for material in bpy.data.materials:
        material.user_clear()
        bpy.data.materials.remove(material)

if __name__ == '__main__':
    print(__file__)

    # Remove all elements
    reset()
    
    current_group = ""
    
    y = -1
    for i, column_info in columns_info.iterrows():
        if column_info["group"] != current_group:
            y += 1
        
        data_column = data[column_info["id"]]
        geom = geoms[column_info["geom"]]
        palette = palettes[column_info["palette"]]
        
        width = draw_column(data_column, y, colors = palette, geom = geom)
        y += width
        
        current_group = column_info["group"]
    
    # Create camera and lamp
    target = utils.target((data.shape[1]/2, y/2, 5))
    utils.camera((-8, -12, 30), target, type='ORTHO', ortho_scale=20)
    utils.lamp((10, -10, 10), target=target, type='SUN')

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Render scene
    
    import os
    print(os.getcwd())
    utils.renderToFolder('rendering', 'funky_cover', 500, 500)
