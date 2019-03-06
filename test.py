from mathutils import Vector, Matrix

objects_to_animate = [values for subdict in columns.values() for values in subdict.values()]

scene = bpy.context.scene

# clear existing animations
scene.frame_set(0)
for obj in objects_to_animate:
    obj.animation_data_clear()
    # obj.scale = Vector((1, 1, 1))
    obj.show_transparent = True
    obj.active_material.use_transparency = True
    obj.active_material.transparency_method = "Z_TRANSPARENCY"
    obj.active_material.alpha = 0.5
    obj.active_material.keyframe_insert(data_path="alpha")

frame_length = 100

for i in range(5):
    frame_ix = i * frame_length + frame_length
    print(frame_ix)
    scene.frame_set(frame_ix)

    for obj in objects_to_animate:
        obj.active_material.alpha = 0.0
        obj.active_material.keyframe_insert(data_path="alpha")

scene.frame_end = i * frame_length

scene.frame_set(0)

