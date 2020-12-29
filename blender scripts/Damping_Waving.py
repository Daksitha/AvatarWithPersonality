# DampAnimationCurves
# Python script for Blender (Tested v2.79)
#
# This script mnipulate the amplitude of the oscilatory movements in animation curve


import bpy
from mathutils import Quaternion
from mathutils import Euler
from mathutils import Vector
import math

from typing import Dict

# Check if the selected object os a MESH
arm_obj = bpy.context.active_object  # type: bpy.types.Object
assert arm_obj.type == 'ARMATURE'
arm = arm_obj.data  # type: bpy.types.Armature
assert isinstance(arm, bpy.types.Armature)


# Weight DB is weights store in a vector for multipling with Eular angles. 
# Take the Quaternion angles from the animation and then convert it to Eular angles. 
# Then multiply these Eular angles with weights to get the desired span of the area
# The reason to convert to Eular angle is basically to track amplitude of the motion is easier in Eular space than Quternion  
# Then convert back to Quternion and store them in animation curves


WEIGHT_DB = {

    #"mixamorig:RightArm": Vector((1.0,1.0,1.0)),
    "mixamorig:RightForeArm": Vector((-10,1.0,1.0)),

}  # type: Dict[str, Vector]





def damp_bone_animation(action: bpy.types.Action, bone_name: str, weights: Vector) -> None:
    """Apply damping effect to the motion

    """
    curve_w = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index =0)  # type: bpy.types.FCurve
    curve_x = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name), index =1)  # type: bpy.types.FCurve
    curve_y = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 2)  # type: bpy.types.FCurve
    curve_z = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 3)  # type: bpy.types.FCurve

    assert curve_w is not None and curve_x is not None and curve_y is not None and curve_z is not None

    # STRONG ASSUMPTION!!!
    # If there is 1 keyframe for the w curve (0) there will be also for the other curves.
    n_keyframes_w = len(curve_w.keyframe_points)
    n_keyframes_x = len(curve_x.keyframe_points)
    n_keyframes_y = len(curve_y.keyframe_points)
    n_keyframes_z = len(curve_z.keyframe_points)

    assert n_keyframes_w == n_keyframes_x == n_keyframes_y == n_keyframes_z

    for i in range(n_keyframes_w):
        kf_w = curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_x = curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_y = curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_z = curve_z.keyframe_points[i]  # type: bpy.types.Keyframe

        # All the time stamps should be the same
        timestamp = kf_w.co[0]
        print("ts {}".format(timestamp))
        print(kf_w.co[0], kf_x.co[0], kf_y.co[0], kf_z.co[0])
        assert kf_w.co[0] == kf_x.co[0] == kf_y.co[0] == kf_z.co[0]

        # Retrieve the current roation
        current_q = Quaternion((kf_w.co[1], kf_x.co[1], kf_y.co[1], kf_z.co[1]))
        current_eulr = current_q.to_euler()
        
        #Element-wise multiplication with a weight vector
        new_euler = Euler((x * y for x, y in zip( weights,current_eulr )), 'XYZ')
        new_q = new_euler.to_quaternion()
      
        #store it back
        kf_w.co[1], kf_x.co[1], kf_y.co[1], kf_z.co[1] = new_q

    # Force timings and handles update
    curve_w.update()
    curve_x.update()
    curve_y.update()
    curve_z.update()
    



def apply_damping_effect(action: bpy.types.Action, db: dict) -> None:
    for bone_name in db.keys():
        # Retrieve the quaternion
        weight_q = db[bone_name]

        print("Applying damp effect {} to bone {}".format(weight_q, bone_name))
        damp_bone_animation(action=action, bone_name=bone_name, weights=weight_q)

print("------------------------------------------------------")
action = arm_obj.animation_data.action
assert action is not None

print("Applying Damping effect...")
apply_damping_effect(action=action, db=WEIGHT_DB)

# Force update of GUI and other properties
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
print("------------------------------------------------------")