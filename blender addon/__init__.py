# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "CAfP",
    "author" : "daksitha",
    "description" : "",
    "blender" : (2, 83, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy 
from bpy.utils import unregister_class
from bpy.utils import register_class
from mathutils import Quaternion
from mathutils import Euler
from mathutils import Vector
import math

def update_func(self, context):
    print("my test function", self)
    bpy.ops.cafp.offsetanimation()
#bpy.types.PoseBone.prop = FloatProperty(default=0.0, description="Change to Update", update=update)

bpy.types.PoseBone.damping_vector = bpy.props.FloatVectorProperty(
        name = "Euler Damping Vector",
        description="damping factor for each axis x,y,z",
        default=(1.0, 1.0, 1.0), 
        soft_min = 0.1, # float
        soft_max  = 2.0,
        update = update_func
    )

def damp_bone_animation(action: bpy.types.Action, bone_name: str, weights: Vector, tail_crop=0, head_crop=0, start=0) -> None:
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

    #Select the range of the animation
    minKeyframe = start+tail_crop
    maxKeyframe = (n_keyframes_w) - head_crop

    for i in range(minKeyframe,maxKeyframe):
        kf_w = curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_x = curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_y = curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_z = curve_z.keyframe_points[i]  # type: bpy.types.Keyframe

        # All the time stamps should be the same
        timestamp = kf_w.co[0]

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




class OffsetAnimation(bpy.types.Operator):
    """Rotational translate animation curves"""
    bl_idname = "cafp.offsetanimation"
    bl_label = "Rotational translate animation curves for the selected bone from the active action"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        if not (context.mode == 'POSE'):
            print("Warning(CAfP): go to pose mode")
            return False

        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            if obj.type == 'ARMATURE':
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        return True
        print("Warning(CAfP): There are no active animation action")
        return False

    def execute(self, context):
        import re

        # Active Armature
        obj = context.active_object  # type: bpy.types.Object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'},"Selected object {} is not ARMATURE type".format(obj))
            return {'CANCELLED'}
    
        #active item 
        #item = obj.data.bones.active
        #print("item_activate: {}".format(item.basename))
        #print("item_activate children: {}".format(item.children_recursive_basename))
        #print("item_activate parent: {}".format(item.parent_recursive))

        active_bone = bpy.context.active_pose_bone
        bone_name = active_bone.basename
        #animation
        #TODO: mkeep the original animation and alter every changes from the original
        action = obj.animation_data.action
        if active_bone is not None:
            
            weights = active_bone.damping_vector
            if action is not None:
                
                #weights = Vector((1,1,1))
                damp_bone_animation(action, bone_name, weights) 
            else:
                self.report({'ERROR'},"Armature {0} has no animation data".format(obj))
                return {'CANCELLED'}
        else:
            self.report({'ERROR'},"No active_bone")
            return {'CANCELLED'}

        return {'FINISHED'}
        
    

class VIEW3D_PT_cafpmainpanle(bpy.types.Panel):
    bl_label = "CAfP_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'objectmode'
    bl_category = "CAfP"

    def draw(self, context):
        layout = self.layout
        active_bone = bpy.context.active_pose_bone

        if context.mode == 'POSE':
            row = layout.row()
            box = row.box()
            box.label(text = "Animation:")
            box.operator(OffsetAnimation.bl_idname, text="Get animation details")
            
            layout.row()
            row2 = layout.row()
            box2 = row2.box()
            box2.label(text = "Damping:")
            if active_bone is not None: 
                box2.prop(active_bone, "damping_vector",toggle=True)
            else: 
                infor_messsage = box2.row()
                infor_messsage.label(text= "select a single bone")

        else:
            layout.label(text = 'Please go to the Pose mode') 
            

        


        





classes = (VIEW3D_PT_cafpmainpanle,OffsetAnimation)

def register():
    for clas in classes:
        register_class(clas)

def unregister():
    for clas in reversed(classes):
        unregister_class(clas)
