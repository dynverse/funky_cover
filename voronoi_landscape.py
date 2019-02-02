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
def extrude_face_upwards(bm, face, extrusion):
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    f = r['faces'][0]
    bmesh.ops.translate(bm, vec=Vector((0, 0, extrusion)), verts=f.verts)
    
    return f

def extrude_edge_upwards(bm, face, extrusion):
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    f = r['faces'][0]
    bmesh.ops.translate(bm, vec=Vector((0, 0, extrusion)), verts=f.verts[-2:])
    
    return f

def geom_funkyrect(bm, x, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([x - w * datum / 2 + 0.5, 0.5 - w * datum / 2,0]),
        bm.verts.new([x + w * datum / 2 + 0.5, 0.5 - w * datum / 2,0]),
        bm.verts.new([x + w * datum / 2 + 0.5, 0.5 + w * datum / 2,0]),
        bm.verts.new([x - w * datum / 2 + 0.5, 0.5 + w * datum / 2,0])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_rect(bm, x, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([x, 0, 0]),
        bm.verts.new([x + 1, 0, 0]),
        bm.verts.new([x + 1, 1,0]),
        bm.verts.new([x, 1,0])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_circle(bm, x, datum, h = 10, r = 0.5):
    face = bm.faces.new([
        bm.verts.new([x + np.cos(theta) * r * datum + r, 0 + np.sin(theta) * r * datum + r, 0])
        for theta in np.arange(0, np.pi * 2, 0.05)
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_bar(bm, x, datum, h = 10, w = 4):
    face = bm.faces.new([
        bm.verts.new([x, 0, 0]),
        bm.verts.new([x + 1, 0, 0]),
        bm.verts.new([x + 1, datum * w, 0]),
        bm.verts.new([x, datum * w, 0])
    ])
    
    #face = extrude_edge_upwards(bm, face, datum * h)
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, w)

def create_object(bm, x = 0, y = 0, z = 0):
    me = bpy.data.meshes.new("VornoiMesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Voronoi", me)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()
    
    # move obj
    obj.location = obj.location + Vector((x, y, z))
    
    return obj

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
            face.material_index = idx
            for edge in face.edges:
                for f in edge.link_faces:
                    f.material_index = idx
    
    # create object
    obj = create_object(bm, y = y)

    # Create and assign materials to object
    for color in colors:
        mat = bpy.data.materials.new('Material')
        mat.diffuse_color = color
        mat.diffuse_intensity = 0.9
        obj.data.materials.append(mat)
        
    return width

def draw_group(y_start, y_end, width, palette):
    # create mesh
    bm = bmesh.new()
    
    height = y_end - y_start
    x = width
    
    floor = bm.faces.new([
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([x+0.5, 0, 0]),
        bm.verts.new([x+0.5, height, 0]),
        bm.verts.new([-0.5, height, 0])
    ])
    carpet = bm.faces.new([
        bm.verts.new([x+0.5, 0, -100]),
        bm.verts.new([x+0.5, 0, 0]),
        bm.verts.new([x+0.5, height, 0]),
        bm.verts.new([x+0.5, height, -100])
    ])
    curtain = bm.faces.new([
        bm.verts.new([-0.5, 0, 100]),
        bm.verts.new([-0.5, 0, 0]),
        bm.verts.new([-0.5, height, 0]),
        bm.verts.new([-0.5, height, 100])
    ])
    
    obj = create_object(bm, y = y_start)
    
    # add color
    color = palette[np.int(np.floor(len(palette)/4))]
    
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.9
    obj.data.materials.append(mat)

def reset():
    # remove objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=True)
    
    # remove materials
    for material in bpy.data.materials:
        #material.user_clear()
        bpy.data.materials.remove(material)

if __name__ == '__main__':
    print(__file__)

    # Remove all elements
    reset()
    
    # print columns
    w = data.shape[0] # width of data
    
    groups = []
    current_group = None
    current_group_y_start = 0
    
    y = 0
    for i, column_info in columns_info.iterrows():        
        data_column = data[column_info["id"]]
        geom = geoms[column_info["geom"]]
        palette = palettes[column_info["palette"]]
        
        width = draw_column(data_column, y, colors = palette, geom = geom)
        y += width
        
        # end of current group -> add to groups and augment y
        if i == columns_info.shape[0]-1 or column_info["group"] != columns_info.group[i+1]:
            groups.append({
                "y_start": current_group_y_start, 
                "y_end": y,
                "id": current_group
            })
            y += 1
            current_group_y_start = y
        
        current_group = column_info["group"]
        
    print(groups)
    # plot groups
    for group in groups:
        group_info = columns_groups.ix[columns_groups.group == group["id"]].to_dict(orient = "records")[0]
        
        print(group_info)
        
        draw_group(
            group["y_start"], 
            group["y_end"], 
            w, 
            palettes[group_info["palette"]]
        )
    
    # Create camera and lamp
    h = y
    
    target = utils.target((w/2, h/2, 5))
    utils.lamp((w + 10, h + 10, 20), target=target, type='SUN')
    utils.camera((w + w/2, h/2+h/4, 50), target = target, type='ORTHO', ortho_scale=y)

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Render scene
    utils.renderToFolder('rendering', 'funky_cover', 2400/4, 3150/4)
