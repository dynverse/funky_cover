import bpy
import bmesh
import numpy as np
import pandas as pd
from random import random
from mathutils import Vector, Matrix
import colorsys
import utils
import os

import json

font = bpy.data.fonts.load(filepath = os.path.abspath("design/hind-bold.ttf"))

print(font)

# load in dynbenchmark data
column_infos = pd.read_csv("data/column_infos.csv")
group_infos = pd.read_csv("data/group_infos.csv")
experiment_infos = pd.read_csv("data/experiment_infos.csv")
#group_infos = experiment_infos
row_infos = pd.read_csv("data/row_infos.csv")
rowgroup_infos = pd.read_csv("data/rowgroup_infos.csv")

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

def geom_funkyrect(bm, y, z, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([-w * datum / 2 + 0.5, y + 0.5 - w * datum / 2,z]),
        bm.verts.new([+w * datum / 2 + 0.5, y + 0.5 - w * datum / 2,z]),
        bm.verts.new([+w * datum / 2 + 0.5, y + 0.5 + w * datum / 2,z]),
        bm.verts.new([-w * datum / 2 + 0.5, y + 0.5 + w * datum / 2,z])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_rect(bm, y, z, datum, h = 10, w = 1):
    face = bm.faces.new([
        bm.verts.new([0, y+0, z]),
        bm.verts.new([1, y+0, z]),
        bm.verts.new([1, y+1, z]),
        bm.verts.new([0, y+1, z])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_circle(bm, y, z, datum, h = 10, r = 0.5):
    face = bm.faces.new([
        bm.verts.new([x + np.cos(theta) * r * datum + r, 0 + np.sin(theta) * r * datum + r, z])
        for theta in np.arange(0, np.pi * 2, 0.05)
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, 1)

def geom_bar(bm, y, z, datum, h = 10, w = 4):
    face = bm.faces.new([
        bm.verts.new([0, y, z]),
        bm.verts.new([0, y + 1, z]),
        bm.verts.new([datum * w, y + 1, z]),
        bm.verts.new([datum * w, y, z])
    ])
    
    #face = extrude_edge_upwards(bm, face, datum * h)
    face = extrude_face_upwards(bm, face, datum * h)
    
    return (face, w)

def create_object(bm, x = 0, y = 0, z = 0):
    me = bpy.data.meshes.new("ColumnMesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("Column", me)
    bpy.context.scene.objects.link(obj)
    
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
def draw_column(data, row_infos, x = 1, palette = "benchmark", geom = geom_rect):
    colors = palettes[palette]
    
    bm = bmesh.new()
    
    top_faces = []
    
    # create meshes
    for (i, row_info), datum in zip(row_infos.iterrows(), data):
        y = row_info["y"]
        z = row_info["z"]
        if not np.isnan(datum):
            # ground face
            face, width = geom(bm, y, z, datum + 0.001)
            
            # extrude
            top_faces.append(face)
        else:
            top_faces.append("")

    # Assign material index to each bar
    for face, datum in zip(top_faces, data):
        if face != "":
            if palette == "benchmark":
                modifier = 1
            else:
                modifier = 0.5
            idx = np.int(np.floor((len(colors)-1) * (datum**2)*modifier))
            face.material_index = idx
            for edge in face.edges:
                for f in edge.link_faces:
                    f.material_index = idx
    
    # create object
    obj = create_object(bm, x = x)

    # Create and assign materials to object
    for color in colors:
        mat = bpy.data.materials.new('Material')
        mat.diffuse_color = color
        mat.diffuse_intensity = 0.9
        obj.data.materials.append(mat)
        
    return width

def draw_group(x, rowgroup_infos, width, height, palette, b = 0):
    # create mesh
    bm = bmesh.new()
    
    # carpet
    z = rowgroup_infos["z"].iloc[0]
    y = - 0.5
    carpet = bm.faces.new([
        bm.verts.new([0, y, z]),
        bm.verts.new([width, y, z]),
        bm.verts.new([width, y, -100]),
        bm.verts.new([0, y, -100])
    ])
    
    # floors for each group
    for i, rowgroup_info in rowgroup_infos.iterrows():
        y_start = rowgroup_info["y"]-0.5
        y_end = rowgroup_info["y"]+rowgroup_info["height"]+0.5
        z = rowgroup_info["z"]
        floor = bm.faces.new([
            bm.verts.new([0, y_start, z]),
            bm.verts.new([width, y_start, z]),
            bm.verts.new([width, y_end, z]),
            bm.verts.new([0, y_end, z])
        ])
        
    # connections between each group
    for ((i, rowgroup_info), (j, rowgroup_info2)) in zip(rowgroup_infos.iloc[:-1].iterrows(), rowgroup_infos.iloc[1:].iterrows()):
        y = rowgroup_info2["y"]-0.5
        z_start = rowgroup_info["z"]
        z_end = rowgroup_info2["z"]
        floor = bm.faces.new([
            bm.verts.new([0, y, z_start]),
            bm.verts.new([width, y, z_start]),
            bm.verts.new([width, y, z_end]),
            bm.verts.new([0, y, z_end])
        ])
        
    # curtain
    z = rowgroup_infos["z"].iloc[-1]
    y = rowgroup_infos["y"].iloc[-1] + rowgroup_infos["height"].iloc[-1] + 0.5
    curtain = bm.faces.new([
        bm.verts.new([0, y, z]),
        bm.verts.new([width, y, z]),
        bm.verts.new([width, y, 100]),
        bm.verts.new([0, y, 100])
    ])
    
    obj = create_object(bm, x = x, y = b, z = -b)
    
    # add color
    color = palette[np.int(np.floor(len(palette)/4))]
    
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.4
    obj.data.materials.append(mat)
    
def draw_experiment_label(experiment_info):
    # define some positions and parameters
    x = experiment_info["x"] + experiment_info["width"]/2
    y = -0.51
    z = -2
    z_text_offset = 0.5
    width = experiment_info["width"]
    depth = 2
    extrusion = 1
    
    # add text
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.font = font
    obj.data.body = experiment_info["experiment"]
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.edit_format.use_bold = True
    obj.location = Vector((x, y-extrusion-0.05, z+z_text_offset))
    obj.rotation_euler = Vector((np.pi/2, 0, 0))
    obj.data.size = 1.7
    
    color = palettes[experiment_info["palette"]][0]
    
    # text color
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.4
    obj.data.materials.append(mat)
    
    # draw box
    bm = bmesh.new()
    face = bm.faces.new([
        bm.verts.new([x - width/2, y, z - depth/2]),
        bm.verts.new([x + width/2, y, z - depth/2]),
        bm.verts.new([x + width/2, y, z + depth/2]),
        bm.verts.new([x - width/2, y, z + depth/2])
    ])
    
    # extrude
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
    f = r['faces'][0]
    bmesh.ops.translate(bm, vec=Vector((0, -extrusion, 0)), verts=f.verts)
    
    obj = create_object(bm)
    
    # box color
    color = [1,1,1]
    
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.7
    obj.data.materials.append(mat)
    
    return obj

def reset():
    # remove objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=True)
    
    # remove materials
    for material in bpy.data.materials:
        ""
        #material.user_clear()
        #bpy.data.materials.remove(material)

if __name__ == '__main__':
    print(__file__)

    # Remove all elements
    reset()

    bpy.data.worlds["World"].horizon_color = [0.04, 0.04, 0.04]
    
    # plot columns
    w = column_infos.x.iloc[-1] + column_infos.width.iloc[-1] # width of data
    h = data.shape[0]
    d = rowgroup_infos.z.iloc[-1]
    
    for i, column_info in column_infos.iterrows(): 
        ""       
        data_column = data[column_info["id"]]
        geom = geoms[column_info["geom"]]
        palette = column_info["palette"]
        x = column_info["x"]
        width = column_info["width"]
        
        draw_column(data_column, row_infos, x, palette = palette, geom = geom)
    
    # plot group steps
    for i, group_info in group_infos.iterrows():
        ""
        draw_group(
            group_info["x"], 
            rowgroup_infos,
            group_info["width"], 
            h, 
            palettes[group_info["palette"]]
        )
    
    # plot background steps
    draw_group(
        -100,
        rowgroup_infos,
        200,
        h,
        [[0.15, 0.15, 0.15]],
        b = 0.01
    )
    
    # plot experiment labels
    for i, experiment_info in experiment_infos.iterrows():
        draw_experiment_label(experiment_info)

    
    # Create lamp
    target = utils.target((2/3 * w, h/2, d*3.4/4))
    utils.lamp((w + 10, -20, 50), target=target, type='SUN', shadow = True)

    # Choose either camera
    # orthographic camera
    target = utils.target((w/2, h/2, d*3.4/4))
    utils.camera((3/4 * w, -30, 50), target = target, type='ORTHO', ortho_scale=w*1.5)
    
    # perspective camera
    # target = utils.target((w/2, h/2, d*1/2))
    # utils.camera((6/10 * w, -30, 50), target = target, lens = 20)
    
    # update scene
    bpy.context.scene.update()

    # Enable ambient occlusion
    utils.setAmbientOcclusion(samples=10)

    # Render scene
    utils.renderToFolder('rendering', 'funky_cover', 8.5*300, 11*300)
