# OffsetAnimationCurves
# Python script for Blender (Tested v2.79)
#
# This script takes the current action and applies time scaling to the animation keyframes
# This script is only limited to generate the slowmotion by duplicating the number of keyframes by a given factor
#



import bpy

from mathutils import Quaternion
from mathutils import Euler
from mathutils import Vector
import math

from typing import Dict

# Check if the selected object os a MESH

assert arm_obj.type == 'ARMATURE'
arm = arm_obj.data  # type: bpy.types.Armature

assert isinstance(arm, bpy.types.Armature)




def timewarp_bone_animation(action: bpy.types.Action, bone_name: str, factor: float) -> None:
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
    #print('Check: ', curve_w.keyframe_points[:])
    
    #define new set of curves
    updated_curve_w = []
    updated_curve_x = []
    updated_curve_y = []
    updated_curve_z = []

    assert n_keyframes_w == n_keyframes_x == n_keyframes_y == n_keyframes_z
    
    #define the range that need the effect
    warping_start = 20
    warping_end = 80
    
    for i in range(n_keyframes_w):
        
        kf_w = curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_x = curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_y = curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_z = curve_z.keyframe_points[i]  # type: bpy.types.Keyframe
        
        # duplicate the keyframe by factor amount given as a parameter
        for j in range(factor):
            updated_curve_w.append(kf_w)
            updated_curve_x.append(kf_x)
            updated_curve_y.append(kf_y)
            updated_curve_z.append(kf_z)
            
        # All the time stamps should be the same
        timestamp = kf_w.co[0]
        #print("ts {}".format(timestamp))
        # print(kf_w.co[0], kf_x.co[0], kf_y.co[0], kf_z.co[0])
        assert kf_w.co[0] == kf_x.co[0] == kf_y.co[0] == kf_z.co[0]
        
    #check the size of the updated keyframes
    n_updated_w = len(updated_curve_w)
    n_updated_x = len(updated_curve_x)
    n_updated_y = len(updated_curve_y)
    n_updated_z = len(updated_curve_z)
    print(n_updated_w,n_updated_x,n_updated_y,n_updated_z)
 

   #update the original keyframes with updated 
    for f in range(n_updated_w):
        kf_uw = updated_curve_w[f]  # type: bpy.types.Keyframe
        kf_ux = updated_curve_x[f]  # type: bpy.types.Keyframe
        kf_uy = updated_curve_y[f]  # type: bpy.types.Keyframe
        kf_uz = updated_curve_z[f]  # type: bpy.types.Keyframe
        #print(kf_uw.co[1], kf_ux.co[1], kf_uy.co[1], kf_uz.co[1])
        #insert new frames and update current frames
        curve_w.keyframe_points.insert(f, kf_uw.co[1], options={'REPLACE','NEEDED'})
        curve_x.keyframe_points.insert(f, kf_ux.co[1], options={'REPLACE','NEEDED'})
        curve_y.keyframe_points.insert(f, kf_uy.co[1], options={'REPLACE','NEEDED'})
        curve_z.keyframe_points.insert(f, kf_uz.co[1], options={'REPLACE','NEEDED'})
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


action = arm_obj.animation_data.action
assert action is not None

print("Applying slowing effect...")
for bone in arm_obj.data.bones.values():
    print(bone.name)
    try:
        timewarp_bone_animation(action=action,bone_name=bone.name,factor=2)
    except:
        print('\n' +'Bone had some error warping') 
 


# Force update of GUI and other properties
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
