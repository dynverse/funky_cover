from mathutils import Vector, Matrix


scene = bpy.context.scene

###
objects_to_animate = [values for subdict in column_infos.query("group != 'score_overall'").objects for values in subdict.values()]

frame_length = 100

# clear existing animations
scene.frame_set(0)
for obj in objects_to_animate:
    obj.animation_data_clear()
    obj.active_material.keyframe_insert(data_path="diffuse_color")
    obj.data["diffuse_color"] = obj.active_material.diffuse_color

for i in range(2):
    frame_ix = i * frame_length + frame_length
    print(frame_ix)
    scene.frame_set(frame_ix)

    for obj in objects_to_animate:
        obj.active_material.diffuse_color = utils.lighten_color(obj.active_material.diffuse_color, 0.1)
        obj.active_material.keyframe_insert(data_path="diffuse_color")

scene.frame_end = frame_ix

####################

## Move camera to left
scene.frame_set(0)
camera.animation_data_clear()

frame_length = 100
to_track = column_infos.objects[0][row_infos.id.iloc[-1]]
utils.trackToConstraint(camera, to_track)

scene.frame_set(0)
camera.keyframe_insert(data_path = "location")

scene.frame_set(frame_length)
camera.location = Vector((column_infos.x[0], camera.location[1], row_infos.z.iloc[0] * 3))
camera.keyframe_insert(data_path = "location")

## Move method names
objects_to_animate = column_infos.query("id == 'method_name'").objects[0].values()

frame_start = frame_length
frame_end = frame_start + frame_length
for obj in objects_to_animate:
    frame_offset = np.random.randint(0, 20)

    scene.frame_set(frame_end + frame_offset)
    original_location = Vector(obj.data["location"])
    obj.animation_data_clear()

    scene.frame_set(frame_start + frame_offset)
    obj.location = original_location + Vector((-10, 0, 0))
    obj.keyframe_insert("location")

    scene.frame_set(frame_end + frame_offset)
    obj.location = original_location
    obj.keyframe_insert("location")

scene.frame_end = frame_end + frame_length