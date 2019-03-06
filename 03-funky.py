from collections import OrderedDict

# ─── LOAD DATA ──────────────────────────────────────────────────────────────────

funky_container = bpy.data.objects.new("stage_title", None)
funky_container.parent = stage_funky
scene.objects.link(funky_container)

column_infos = pd.read_csv("data/column_infos.csv")
group_infos = pd.read_csv("data/group_infos.csv")
experiment_infos = pd.read_csv("data/experiment_infos.csv")
row_infos = pd.read_csv("data/row_infos.csv")
rowgroup_infos = pd.read_csv("data/rowgroup_infos.csv")

data = pd.read_csv("data/data.csv")

# define palettes
palettes = json.load(open("data/palettes.json"))

palettes = {
    name:[utils.hex_to_rgb(hex) for hex in palette]
    for name, palette in palettes.items()
}
palettes[np.nan] = []

# define palette materials
def create_palette_materials(palette):
    materials = []
    for color in palette:
        mat = bpy.data.materials.new('Material')
        mat.diffuse_color = color
        mat.diffuse_intensity = 0.9
        materials.append(mat)

    return materials
palette_materials = {name:create_palette_materials(palette) for name, palette in palettes.items()}

# ─── PLOT COLUMNS ───────────────────────────────────────────────────────────────

# plot columns
w_overall = column_infos.x.iloc[-1] + column_infos.w.iloc[-1] # width of data
h_overall = data.shape[0]
d_overall = rowgroup_infos.z.iloc[-1]

columns = []
for i, column_info in column_infos.iterrows(): 
    ""       
    data_column = data[column_info["id"]]
    geom = objects.geoms[column_info["geom"]]
    materials = palette_materials[column_info["palette"]]
    x = column_info["x"]
    w = column_info["w"]
    
    column = objects.draw_column(
        data = data_column, 
        row_infos = row_infos, 
        x = x, 
        w = w, 
        materials = materials, 
        geom = geom
    )
    column.parent = funky_container
    columns.append(column)
column_infos["objects"] = columns

# plot group steps
groups = []
for i, group_info in group_infos.iterrows():
    if group_info["group"] != "method_characteristic":
        group = objects.draw_group(
            x = group_info["x"], 
            rowgroup_infos = rowgroup_infos,
            width = group_info["w"], 
            height = h_overall, 
            palette = palettes[group_info["palette"]],
        )
        group.parent = funky_container
        groups.append(group)
    else:
        groups.append(None)
group_infos["object"] = groups


# plot background steps
background_steps = objects.draw_group(
    x = -10000,
    rowgroup_infos = rowgroup_infos,
    width = 20000,
    height = h_overall,
    palette = [[0.15, 0.15, 0.15]],
    b = 0.01
)
background_steps.parent = funky_container

# plot experiment labels
experiment_labels = {}
for i, experiment_info in experiment_infos.iterrows():
    if experiment_info["experiment"] != "Method":
        experiment_label = objects.draw_experiment_label(
            experiment_info
        )
        experiment_label.parent = funky_container
        experiment_labels[experiment_info["experiment"]] = experiment_label

funky_container.location.z -= d_overall/2
funky_container.location.x -= w_overall/2

# ─── ANIMATION ──────────────────────────────────────────────────────────────────

cur_frame = stage_funky["start"]
scene.frame_set(cur_frame)
camera.data.lens = 20

# move camera to the left
nframes = 100
to_track = column_infos.objects[0][row_infos.id.iloc[np.int(np.ceil(row_infos.shape[0]/2))]]

camera.keyframe_insert("location", frame = cur_frame)
camera.keyframe_insert("rotation_euler", frame = cur_frame)

camera.location.y = to_track.matrix_world.to_translation().y
camera.location.z = d_overall * 2
camera.location.x = stage_funky.location.x - d_overall * 2

utils.look_at(camera, to_track)

cur_frame += nframes 
camera.keyframe_insert("location", frame = cur_frame)
camera.keyframe_insert("rotation_euler", frame = cur_frame)

# ─── METHOD NAMES ───────────────────────────────────────────────────────────────
objects_to_animate = column_infos.query("id == 'method_name'").objects[0].values()

nframes = 100
frame_offset = 10
frame_start = cur_frame
frame_end = frame_start + nframes
for i, obj in enumerate(objects_to_animate):
    original_location = Vector(obj.data["location"])

    obj.hide = True
    obj.keyframe_insert("hide", frame = frame_start)
    obj.hide = False
    obj.keyframe_insert("hide", frame = frame_start + 1)

    obj.location = original_location + Vector((-50, 0, 0))
    obj.keyframe_insert("location", frame = frame_start + frame_offset * i)
    
    obj.location = original_location
    obj.keyframe_insert("location", frame = frame_end + frame_offset * i)

cur_frame = frame_end + frame_offset * i

# ─── EVALUATION METRICS ─────────────────────────────────────────────────────────

# move and pan camera to right
nframes = 100

camera.keyframe_insert("location", frame = cur_frame)
camera.keyframe_insert("rotation_euler", frame = cur_frame)

camera.location.y = funky_container.matrix_world.to_translation().y - w_overall/2
camera.location.x = stage_funky.location.x - d_overall * 4

scene.update()
utils.look_at(camera, point = Vector((funky_container.matrix_world.to_translation().x, camera.location.y, funky_container.matrix_world.to_translation().z)))

cur_frame += nframes 
camera.keyframe_insert("location", frame = cur_frame)
camera.keyframe_insert("rotation_euler", frame = cur_frame)

# show experiment labels one by one
nframes = 20
frame_offsets = OrderedDict([
    ["Accuracy", 30],
    ["Scalability", 30],
    ["Stability", 30],
    ["Usability", 100],
    ["Summary", 0]
])
frame_start = cur_frame
for experiment_id, frame_offset in frame_offsets.items():
    groups = group_infos.query("experiment == '" + experiment_id + "'")["object"]
    experiment_label = experiment_labels[experiment_id]

    original_location = Vector((0,0,0))

    # start
    hide(experiment_label, to_hide = True, frame = frame_start)
    hide(experiment_label, to_hide = False, frame = frame_start + 1)

    experiment_label.location = original_location + Vector((0, -30, 0))
    experiment_label.keyframe_insert("location", frame = frame_start)

    for group in groups:
        obj = group.children[0]

        obj.show_transparent = True
        mat = obj.active_material
        mat.use_transparency = True
        mat.transparency_method = "Z_TRANSPARENCY"
        mat.alpha = 0
        mat.keyframe_insert(data_path="alpha", frame = frame_start)
    
    # next
    frame_start += nframes
    experiment_label.location = original_location
    experiment_label.keyframe_insert("location", frame = frame_start)

    for group in groups:
        obj = group.children[0]
        mat = obj.active_material

        mat.alpha = 1
        mat.keyframe_insert(data_path="alpha", frame = frame_start)

    frame_start += frame_offset

cur_frame = frame_start

stage_funky["end"] = cur_frame + 100