# create title and authors
title = objects.text("A comparison of single-cell \ntrajectory inference methods", size = 1.7, parent = stage_title)

rc = objects.text("Robrecht Cannoodt", parent = stage_title)
ws = objects.text("Wouter Saelens", parent = stage_title)
ht = objects.text("Helena Todorov", parent = stage_title)
ys = objects.text("Yvan Saeys", parent = stage_title)

for obj in [rc, ws, ht, ys]:
    obj.location.z -= 4
rc.location.x = -10
ws.location.x = -10
ht.location.x = 0
ys.location.x = 10

# add rc/ws keyframes
base_location = rc.location.copy()
period = 60
for i in range(period):
    scene.frame_set(i)

    radians = i / period * 2 * np.pi
    rc.location = base_location + Vector((0, np.cos(radians), np.sin(radians)))
    rc.keyframe_insert("location")
    
    radians = radians + np.pi
    ws.location = base_location + Vector((0, np.cos(radians), np.sin(radians)))
    ws.keyframe_insert("location")
animation.modify_cyclic_fcurve(rc)
animation.modify_cyclic_fcurve(ws)

stage_title["end"] = period * 3