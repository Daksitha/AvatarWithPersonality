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

gui_status = "ACTIVE_SESSION"
gui_err_msg = ""

def update_func(self, context):
    #print("my test function", self)
    bpy.ops.cafp.offsetanimation()
#bpy.types.PoseBone.prop = FloatProperty(default=0.0, description="Change to Update", update=update)

bpy.types.PoseBone.damping_vector = bpy.props.FloatVectorProperty(
        name = "Euler Damping Vector",
        description="damping factor for each axis x,y,z",
        default=(1.0, 1.0, 1.0), 
        soft_min = -10.0, # float
        soft_max  = 10.0,
        update = update_func
    )

def damp_bone_animation(self, act: bpy.types.Action, bone_name: str, weights: Vector, tail_crop=0, head_crop=0, crop_start=0) -> None:
    """Apply damping effect to the motion
    """
    global gui_status, gui_err_msg

    armature_action = act
    #all actions in the blender scene 
    all_actions = bpy.data.actions
    #CAfP_org_ is the standard prefix for saving the original action
    #This is important when we apply the changes to the existing action
    dummy_name ="CAfP_org_{}".format(armature_action.name)
    dummy_exist_bool =  [act for act in all_actions if act.name.startswith(dummy_name)]

    if not dummy_exist_bool:
        print("creating a dummy of the original action...")
        copy_anim = armature_action.copy()
        copy_anim.name = dummy_name
        copy_anim.use_fake_user = True

    #The original animation will be used as the base animation. 
    #all changes will be added to this 
    #Otherwise changes accumulate and result distrotered fcurve 
    original_action = bpy.data.actions[dummy_name]

    #base actions
    base_curve_w = original_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index =0)  # type: bpy.types.FCurve
    base_curve_x = original_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name), index =1)  # type: bpy.types.FCurve
    base_curve_y = original_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 2)  # type: bpy.types.FCurve
    base_curve_z = original_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 3)  # type: bpy.types.FCurve
    #these are the curves to be changed 
    curve_w = armature_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index =0)  # type: bpy.types.FCurve
    curve_x = armature_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name), index =1)  # type: bpy.types.FCurve
    curve_y = armature_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 2)  # type: bpy.types.FCurve
    curve_z = armature_action.fcurves.find('pose.bones["{0}"].rotation_quaternion'.format(bone_name),index = 3)  # type: bpy.types.FCurve

    #We don't need to check both sets of curves belwo.  
    if(curve_w is None and curve_x is None and curve_y is None and curve_z is None and \
        base_curve_w is None and base_curve_x is None and base_curve_y is None and base_curve_z is None):

        self.report({'ERROR'},"Selected bone has no animation data,pick a bone with animation data")
        gui_status = 'ERROR_SESSION'
        gui_err_msg = 'Selected bone has no animation data, pick a bone with animation data'
        return 
    else:
        gui_status = 'ACTIVE_SESSION'


    # STRONG ASSUMPTION!!!
    # If there is 1 keyframe for the w curve (0) there will be also for the other curves.
    base_kf_w = len(curve_w.keyframe_points)
    base_kf_x = len(curve_x.keyframe_points)
    base_kf_y = len(curve_y.keyframe_points)
    base_kf_z = len(curve_z.keyframe_points)
    #action curves
    n_keyframes_w = len(curve_w.keyframe_points)
    n_keyframes_x = len(curve_x.keyframe_points)
    n_keyframes_y = len(curve_y.keyframe_points)
    n_keyframes_z = len(curve_z.keyframe_points)

    #assert n_keyframes_w == n_keyframes_x == n_keyframes_y == n_keyframes_z == base_kf_w == base_kf_x == base_kf_y == base_kf_z
    if not (n_keyframes_w == n_keyframes_x == n_keyframes_y == \
        n_keyframes_z == base_kf_w == base_kf_x == base_kf_y == base_kf_z):
        self.report({'ERROR'}, 'All Fcurves for {} must have {} equal number of keyframes'.format(armature_action.name,n_keyframes_w))
        gui_status = 'ERROR_SESSION'
        gui_err_msg = 'All Fcurves for {} must have {} equal number of keyframes'.format(armature_action.name,n_keyframes_w)
        return 
    else:
        gui_status = 'ACTIVE_SESSION'


    #Select the range of the animation
    if( (crop_start+tail_crop <n_keyframes_w-crop_start) and \
        (n_keyframes_w-crop_start > head_crop) ):
        minKeyframe = crop_start+tail_crop
        maxKeyframe = (n_keyframes_w) - head_crop
        #self.report({'INFO'}, "Damping effect applies to keyframes from {0} till {1}".format(minKeyframe,maxKeyframe))
    else:
        minKeyframe = 0
        maxKeyframe = n_keyframes_w
        self.report({'WARNING'}, "Unexpected keyframe crop, applying to all keyframes from {} till {}".format(minKeyframe,maxKeyframe) ) 


    for i in range(minKeyframe,maxKeyframe):

        base_kf_w = base_curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        base_kf_x = base_curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        base_kf_y = base_curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        base_kf_z = base_curve_z.keyframe_points[i]  # type: bpy.types.Keyframe

        kf_w = curve_w.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_x = curve_x.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_y = curve_y.keyframe_points[i]  # type: bpy.types.Keyframe
        kf_z = curve_z.keyframe_points[i]  # type: bpy.types.Keyframe

        # All the time stamps should be the same
        #timestamp = kf_w.co[0]
        #print("timestamp kf: {}".format(timestamp))

        if not(kf_w.co[0] == kf_x.co[0] == kf_y.co[0] == kf_z.co[0]== base_kf_w.co[0] == \
            base_kf_x.co[0] == base_kf_y.co[0] == base_kf_z.co[0]):
            self.report({'ERROR'}, '{} keyframe missing in one of the FCurves'.format(kf_w.co[0]))
            gui_status = 'ERROR_SESSION'
            gui_err_msg = '{} keyframe missing in one of the FCurves'.format(kf_w.co[0])
            return 
        else:
            gui_status = 'ACTIVE_SESSION'


        # Retrieve the base roation
        current_q = Quaternion((base_kf_w.co[1], base_kf_x.co[1], base_kf_y.co[1], base_kf_z.co[1]))
        current_eulr = current_q.to_euler()
        
        #Element-wise multiplication with a weight vector
        new_euler = Euler((x * y for x, y in zip( weights,current_eulr )), 'XYZ')
        new_q = new_euler.to_quaternion()
        
        #update armature action
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
        active_bone = bpy.context.active_pose_bone
        bone_name = active_bone.basename

        #animation
        #TODO: keep the original animation and alter every changes from the original
        action = obj.animation_data.action

        if active_bone is not None:
            
            weights = active_bone.damping_vector
            if action is not None:
                damp_bone_animation(self, action, bone_name, weights)

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
        global gui_err_msg, gui_status

        box_info = self.layout.box()
        box_info.label(text="Animation editor for armature")


        if context.mode == 'POSE':

            if gui_status == "ERROR_SESSION":
                box_err = self.layout.box()
                box_err.label(text=gui_err_msg, icon="INFO")

                row = layout.row()
                box = row.box()
                box.label(text = "Animation:")
                box.operator(OffsetAnimation.bl_idname, text="back")

            if gui_status == "ACTIVE_SESSION":

                
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
            layout.label(text = 'Please go to the Pose mode',icon="INFO") 
            

        


        





classes = (VIEW3D_PT_cafpmainpanle,OffsetAnimation)

def register():
    for clas in classes:
        register_class(clas)

def unregister():
    for clas in reversed(classes):
        unregister_class(clas)
