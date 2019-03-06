import bpy
from mathutils import Vector
import numpy as np

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

font = bpy.data.fonts.load(filepath = os.path.abspath("design/fonts/hind-bold.ttf"))

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

# define different geoms
def geom_funkyrect(bm, y, z, w, datum, h = 10):
    face = bm.faces.new([
        bm.verts.new([-w * datum / 2 + 0.5, y + 0.5 - w * datum / 2,z]),
        bm.verts.new([+w * datum / 2 + 0.5, y + 0.5 - w * datum / 2,z]),
        bm.verts.new([+w * datum / 2 + 0.5, y + 0.5 + w * datum / 2,z]),
        bm.verts.new([-w * datum / 2 + 0.5, y + 0.5 + w * datum / 2,z])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return face

def geom_rect(bm, y, z, w, datum, h = 10):
    face = bm.faces.new([
        bm.verts.new([0, y+0, z]),
        bm.verts.new([1, y+0, z]),
        bm.verts.new([1, y+1, z]),
        bm.verts.new([0, y+1, z])
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return face

def geom_circle(bm, y, z, w, datum, h = 10, r = 0.5):
    face = bm.faces.new([
        bm.verts.new([x + np.cos(theta) * r * datum + r, 0 + np.sin(theta) * r * datum + r, z])
        for theta in np.arange(0, np.pi * 2, 0.05)
    ])
    
    face = extrude_face_upwards(bm, face, datum * h)
    
    return face

def geom_bar(bm, y, z, w, datum, h = 10):
    face = bm.faces.new([
        bm.verts.new([0, y, z]),
        bm.verts.new([0, y + 1, z]),
        bm.verts.new([datum * w, y + 1, z]),
        bm.verts.new([datum * w, y, z])
    ])
    
    #face = extrude_edge_upwards(bm, face, datum * h)
    face = extrude_face_upwards(bm, face, datum * h)
    
    return face

def geom_text(bm, y, z, w, datum):
    # define some positions and parameters
    width = w
    
    # add text
    bpy.ops.object.text_add()
    obj = bpy.context.scene.objects[0]
    obj.data.font = font
    obj.data.body = datum
    obj.data.align_x = "RIGHT"
    obj.data.align_y = "BOTTOM"
    obj.data.edit_format.use_bold = True
    obj.location = Vector((0, 0.5, 1.7/3))
    obj.rotation_euler = Vector((np.pi/2, 0, 0))
    obj.data.size = 1.7
    
    color = [0,0,0]
    
    # text color
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.4
    obj.data.materials.append(mat)
    
    return obj

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
    "bar": geom_bar,
    "text": geom_text
}

# draw a column
def draw_column(data, row_infos, x = 1, w = 1, materials = None, geom = geom_rect):
    # create column parent
    column = bpy.data.objects.new("column", None)
    bpy.context.scene.objects.link(column)

    # create meshes
    for (i, row_info), datum in zip(row_infos.iterrows(), data):
        y = row_info["y"]
        z = row_info["z"]
        if isinstance(datum, str) or not np.isnan(datum):
            # create bmesh
            bm = bmesh.new()

            # create geom
            face = geom(bm, 0, 0, w, datum)

            # create object
            if not isinstance(face, bpy.types.Object):
                obj = create_object(bm, x = x, y = y, z = z)
            else:
                obj = face
                obj.location = obj.location + Vector((x, y, z))
            
            obj.parent = column
            obj.data["location"] = obj.location
            
            if len(materials) > 0:
                modifier = 0.5
                idx = np.int(np.floor((len(materials)-1) * (datum**2)*modifier))
                obj.data.materials.append(materials[idx].copy())

            column[row_info["id"]] = obj

    return column

def draw_group(x, rowgroup_infos, width, height, palette, b = 0):
    # create group
    group = bpy.data.objects.new("group", None)
    bpy.context.scene.objects.link(group)

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
    obj.parent = group
    
    # add color
    color = palette[np.int(np.floor(len(palette)/4))]
    
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.4
    obj.data.materials.append(mat)

    return group
    
def draw_experiment_label(experiment_info):
    # create group
    experiment_label = bpy.data.objects.new("experiment_label", None)
    bpy.context.scene.objects.link(experiment_label)

    # define some positions and parameters
    x = experiment_info["x"] + experiment_info["w"]/2
    y = -0.51
    z = -2
    z_text_offset = 0.5
    width = experiment_info["w"]
    depth = 2
    extrusion = 1
    
    # add text
    bpy.ops.object.text_add()
    obj = bpy.context.scene.objects[0]
    obj.data.font = font
    obj.data.body = experiment_info["experiment"]
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.edit_format.use_bold = True
    obj.location = Vector((x, y-extrusion-0.05, z+z_text_offset))
    obj.rotation_euler = Vector((np.pi/2, 0, 0))
    obj.data.size = 1.7

    obj.parent = experiment_label
    
    color = utils.hex_to_rgb(experiment_info["color"])
    
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

    obj.parent = experiment_label
    
    # box color
    color = [.9,.9,.9]
    
    mat = bpy.data.materials.new('Material')
    mat.diffuse_color = color
    mat.diffuse_intensity = 0.7
    obj.data.materials.append(mat)
    
    return experiment_label

def text(
    body, 
    align_x = "CENTER", 
    align_y = "CENTER", 
    use_bold = True,
    size = 1, 
    extrude = 0.1, 
    scene = bpy.context.scene,
    parent = None,
    font = font
):
    # create text
    fontcurve = bpy.data.curves.new('font', "FONT")
    fontcurve.extrude = extrude
    fontcurve.font = font

    obj = bpy.data.objects.new('text', fontcurve)

    text = obj.data
    text.body = body
    text.align_x = align_x
    text.align_y = align_y
    text.edit_format.use_bold = use_bold
    text.size = size

    scene.objects.link(obj)
    if parent is not None:
        obj.parent = parent

    obj.rotation_euler = Vector((np.pi/2, 0, 0))

    return obj