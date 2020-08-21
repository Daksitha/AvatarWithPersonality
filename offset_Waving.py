# OffsetAnimationCurves
# Python script for Blender (Tested v2.82)
#
# This script apply rotary translation to an animation meaning position of a joint changes 
#during the period of the motion  
# Period of the motion can be divided into START,ACTION,END and are stored in a dictionary 
# Relevent anles in Quaternion are safed in three different dictionaires 
# Apply suitable offset in suitable portion of the animation.



import bpy
from mathutils import Quaternion

import math

from typing import Dict

# Check if the selected object os a MESH
arm_obj = bpy.context.active_object  
assert arm_obj.type == 'ARMATURE'
arm = arm_obj.data 
assert isinstance(arm, bpy.types.Armature)


# DB of offsets.
# { Bone name: Quaternion, ... }
# For each bone, specify the rotation needed to align it with the reference T-pose skeleton downloaded from Mixamo.
# All rotations are in bone local space.
# Hence, when manually looking for the rotaion value,  first adjust bones closer to the root.

   # Offset regions
    #Identify which regionds has the start of the motion and action and then the end of the motion
    # This was important to identify to apply the transformation. Three regions has to be treated differently
    #3 different Dictionaries defined for these regions
    # main motion 25-79 (50-158 after slow motion)
    # start - 0-24 (0-49 after slow motion)
    # end 80- end (158-end after slow motion)


ACTION_RANGE = {
        "START_ANIM": [0,24],
        "ACTION_ANIM" : [25,79],
        "END_ANIM" : [80,90],
}

OFFSETS_DB_ACTION = {
    #rotation order Z Y X
    "mixamorig:RightArm": Quaternion((0,1,0), math.radians(-30))@ Quaternion((1,0,0), math.radians(+30)),
    

}  # type: Dict[str, Quaternion]

OFFSETS_DB_START_ANIMATION = {
    #rotation order Z Y X
    "mixamorig:RightArm": Quaternion((1,0,1), math.radians(+7)),
    "mixamorig:RightForeArm": Quaternion((1,0,1), math.radians(-7)),

    

}  # type: Dict[str, Quaternion]

OFFSETS_DB_END_ANIMATION = {
    #rotation order Z Y X
    "mixamorig:RightArm": Quaternion((1,0,1), math.radians(+7)),
    "mixamorig:RightForeArm": Quaternion((1,0,1), math.radians(-7)),
    

}  # type: Dict[str, Quaternion]



def offset_bone_animation(action: bpy.types.Action, bone_name: str, offset: Quaternion, start_: int , end_: int) -> None:
    """Apply rotation offset to the rotation curves of the given action
       For the moment we handle only quaternions

    """

    curve_w = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index =0) 
    curve_x = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name), index =1)  
    #print(curve_x.array_index)
    curve_y = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 2) 
    curve_z = action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 3) 

    assert curve_w is not None and curve_x is not None and curve_y is not None and curve_z is not None

    # STRONG ASSUMPTION!!!
    # If there is 1 keyframe for the w curve (0) there will be also for the other curves.
    n_keyframes_w = len(curve_w.keyframe_points)
    n_keyframes_x = len(curve_x.keyframe_points)
    n_keyframes_y = len(curve_y.keyframe_points)
    n_keyframes_z = len(curve_z.keyframe_points)

    assert n_keyframes_w == n_keyframes_x == n_keyframes_y == n_keyframes_z
    
 
    
    for i in range(start_,end_):
        kf_w = curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_x = curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_y = curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_z = curve_z.keyframe_points[i]  # type: bpy.types.Keyframe

        # All the time stamps should be the same
        timestamp = kf_w.co[0]
        print("ts {}".format(timestamp))

        # Retrieve the current roation
        current_q = Quaternion((kf_w.co[1], kf_x.co[1], kf_y.co[1], kf_z.co[1]))
        # compute the updated rotation
        new_q = offset @ current_q
        # store it back
        kf_w.co[1], kf_x.co[1], kf_y.co[1], kf_z.co[1] = new_q

    # Force timings and handles update
    curve_w.update()
    curve_x.update()
    curve_y.update()
    curve_z.update()


def apply_offsets(action: bpy.types.Action, off_db: dict, anim_db: dict) -> None:
    i = 0
    start = 0
    end = 0
    #synchronize both animation and offset datasets 
    if off_db == OFFSETS_DB_END_ANIMATION:
        start = anim_db["END_ANIM"][0]
        end = anim_db["END_ANIM"][1]
        print("Animation start at:", start, "and Ends at: ", end)
    elif off_db == ACTION_RANGE:
        start = anim_db["ACTION_ANIM"][0]
        end = anim_db["ACTION_ANIM"][1]
        print("Animation start at:", start, "and Ends at: ", end) 
    elif off_db == OFFSETS_DB_START_ANIMATION:
        start = anim_db["START_ANIM"][0]
        end = anim_db["START_ANIM"][1]
        print("Animation start at:", start, "and Ends at: ", end)

            
    for bone_name in off_db.keys():
        # Retrieve the quaternion
        offset_q = off_db[bone_name]
        i = i+1
        print("{}th case Applying offset {} to bone {}".format(i, offset_q, bone_name))
        offset_bone_animation(action=action, bone_name=bone_name, offset=offset_q, start_=start,end_=end)

print("------------------------------------------------------")
action = arm_obj.animation_data.action
assert action is not None

print("Starting to offset...")

OFFSETS_DB = OFFSETS_DB_END_ANIMATION
ANIMATION_DB = ACTION_RANGE
apply_offsets(action=action, off_db=OFFSETS_DB, anim_db= ANIMATION_DB)

# Force update of GUI and other properties
bpy.context.scene.frame_set(bpy.context.scene.frame_current)
print("------------------------------------------------------")