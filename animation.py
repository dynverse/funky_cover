def modify_cyclic_fcurve(obj):
    for fc in obj.animation_data.action.fcurves.values():
        cycle = fc.modifiers.new(type='CYCLES')

def ease_fcurve(obj, easing = "AUTO", interpolation = 'BEZIER'):
    for fc in obj.animation_data.action.fcurves.values():
        for kfp in fc.keyframe_points:
            kfp.easing = easing
            kfp.interpolation = interpolation
