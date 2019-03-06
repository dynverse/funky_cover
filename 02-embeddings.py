n_datasets = 9
n_cols = 3

# add spheres to embedding
for dataset_ix in range(1, n_datasets + 1):
    # create table element
    element = bpy.data.objects.new("element", None)
    scene.objects.link(element)
    element.parent = stage_embeddings
    
    element.rotation_euler.x = np.pi/2

    # put element in a grid, centered around 0,0,0 (assumes each element has size 1)
    padding = 1.8
    element.location.z = (np.floor((dataset_ix-1) / n_cols) - ((n_cols-1)/2)) * padding
    element.location.x = (((dataset_ix-1) % n_cols) - ((n_cols-1)/2)) * padding

    # create plane background
    dim = 0.45*padding
    vertices = [
        (-dim, -dim, 0.0),
        (-dim, dim, 0.0),
        (dim, dim, 0.0),
        (dim, -dim, 0.0),
    ]
    faces = [(0, 1, 2, 3)]
    mesh = bpy.data.meshes.new("background")
    background = bpy.data.objects.new("background", mesh)

    scene.objects.link(background)
    background.parent = element

    background.location.z = -0.5

    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)

    # create embedding
    embedding = bpy.data.objects.new("embedding", None)
    scene.objects.link(embedding)
    embedding.parent = element

    # animate embedding
    period = 180
    embedding.rotation_euler.y = 0
    embedding.keyframe_insert("rotation_euler", frame = 0)
    embedding.rotation_euler.y = np.pi
    embedding.keyframe_insert("rotation_euler", frame = period/2)
    embedding.rotation_euler.y = np.pi * 2
    embedding.keyframe_insert("rotation_euler", frame = period)
    animation.modify_cyclic_fcurve(embedding)
    animation.ease_fcurve(embedding, interpolation = 'LINEAR')

    embedding_coords = pd.read_csv("data/embeddings/embedding_" + str(dataset_ix) + ".csv")
    for i, coord in embedding_coords.iterrows():
        coord = Vector((coord["comp_1"], coord["comp_2"],coord["comp_3"]))
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.03, location=coord - Vector((0.5, 0.5, 0.5)))
        obj = bpy.context.object
        obj.parent = embedding

    # add trajectory
    trajectory_coords = pd.read_csv("data/embeddings/trajectory_" + str(dataset_ix) + ".csv")

    for group, trajectory_coords_group in trajectory_coords.groupby("group"):
        curve = bpy.data.curves.new('myCurve', type='CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 2
        curve.bevel_depth = 0.05

        polyline = curve.splines.new('POLY')
        polyline.points.add(trajectory_coords_group.shape[0]-1)
        for i, coord in trajectory_coords_group.reset_index().iterrows():
            coord = Vector((coord["comp_1"], coord["comp_2"],coord["comp_3"], 1))
            polyline.points[i].co = coord - Vector((0.5, 0.5, 0.5, 0.5))

        curve = bpy.data.objects.new('myCurve', curve)
        scene.objects.link(curve)
        curve.parent = embedding

stage_embeddings["end"] = stage_embeddings["start"] + 100