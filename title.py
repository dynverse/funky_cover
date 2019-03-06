#### CELLS
stage_cells = bpy.data.objects.new("stage_title", None)
stage_cells.rotation_euler = Vector((0,0,0))
stage_cells.location = Vector((0, 25, 0))
scene.objects.link(stage_cells)
scale = 5
stage_cells.scale = Vector((scale, scale, scale))


# move camera
camera.keyframe_insert("rotation_euler", frame = 100)
utils.look_at(camera, stage_cells)
camera.keyframe_insert("rotation_euler", frame = 200)

bpy.context.scene.frame_set(200)

