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
    "category" : "Animation"
}

import bpy 
from bpy.utils import unregister_class
from bpy.utils import register_class

#from . damping_tools import DampAnimation
#from . offset_tools import AngularOffsetAnimation
from . bone_motion import BoneAnimatorOffDamp

#all global variables are shared accross using Singletone method 
import CAfP.global_config as global_config


def update_bone_animation(self, context):
    print("bone animator", self)
    bpy.ops.cafp.boneanimator()
    


#Define custome property for PoseBone 
# bpy.types.PoseBone.damping_vector = bpy.props.FloatVectorProperty(
#         name = "Bone Damping Vector",
#         description="x,y,z axis oscillation adjustment",
#         default=(1.0, 1.0, 1.0), 
#         min = 0, # float
#         max  = 10.0,
#         step= 0.1,
#         precision= 3,
#         update = update_bone_animation
#     )

#motion curve almplitude damping scales 
#x scale
bpy.types.PoseBone.damping_x_scale = bpy.props.FloatProperty(
        name = "X scale",
        description="motion curve almplitude damping scale x",
        default=1.0, 
        min = 0.0, # float
        max  = 10.0,
        step= 0.1,
        precision= 1,
        update = update_bone_animation
    )
#y scale
bpy.types.PoseBone.damping_y_scale = bpy.props.FloatProperty(
        name = "Y scale",
        description="motion curve almplitude damping scale y",
        default=1.0, 
        min = 0.0, # float
        max  = 10.0,
        step= 0.1,
        precision= 1,
        update = update_bone_animation
    )

#Z scale
bpy.types.PoseBone.damping_z_scale = bpy.props.FloatProperty(
        name = "Z scale",
        description="motion curve almplitude damping scale z",
        default=1.0, 
        min = 0.0, # float
        max  = 10.0,
        step= 0.1,
        precision= 1,
        update = update_bone_animation
    )


## offset 

#x angular offset
bpy.types.PoseBone.angular_offset_x = bpy.props.IntProperty(
        name = "X Offset",
        description="x axis angular offset",
        default=0, 
        soft_min = -180, 
        soft_max  = 180,
        subtype = 'ANGLE',
        update = update_bone_animation
    )
#y angular offset
bpy.types.PoseBone.angular_offset_y = bpy.props.IntProperty(
        name = "Y Offset",
        description="y axis angular offset",
        default=0, 
        soft_min = -180, 
        soft_max  = 180,
        subtype = 'ANGLE',
        update = update_bone_animation
    )
#z angular offset
bpy.types.PoseBone.angular_offset_z = bpy.props.IntProperty(
        name = "Z Offset",
        description="z axis angular offset",
        default=0, 
        soft_min = -180, 
        soft_max  = 180,
        subtype = 'ANGLE',
        update = update_bone_animation
    )

initial_check = False

class VIEW3D_PT_cafpmainpanle(bpy.types.Panel):
    bl_label = "CAfP_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'objectmode'
    bl_category = "CAfP"

  

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        global initial_check

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                anim_data = active_object.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        initial_check = True
                        box_info = self.layout.box()
                        box_info.label(text='Create Armatures for Personality', icon="OUTLINER_OB_ARMATURE")
                        
                    else:
                        box_err = self.layout.box()
                        box_err.label(text='Amature has no animation action', icon="ERROR")     
                else:
                    box_err = self.layout.box()
                    box_err.label(text='Amature has no animation', icon="ERROR")      
            else:
                box_err = self.layout.box()
                box_err.label(text='Object is not ARMATURE type', icon="ERROR")       
        else:
            box_err = self.layout.box()
            box_err.label(text='No active object', icon="ERROR")

        
        #Assume posemode only active for armature types
        if initial_check:
            if context.mode == 'POSE':

                if global_config.gui_status.startswith("ERROR"):

                    if global_config.gui_status == "ERROR_BONE_OPP":
                        box_err = self.layout.box()
                        box_err.label(text=global_config.gui_err_msg, icon="ERROR")
                        row = layout.row()
                        box = row.box()
                        box.label(text = "OFFSET TOOL:")
                        box.operator(BoneAnimatorOffDamp.bl_idname, text="back")
                    else:
                        box_err = self.layout.box()
                        box_err.label(text=global_config.gui_err_msg, icon="ERROR")

                
                if global_config.gui_status.startswith("ACTIVE"):
                    active_bone = bpy.context.active_pose_bone
                    bone_name = active_bone.basename
                    layout.row()
                    layout.row().label(text="Active Bone: {}".format(bone_name), icon= 'BONE_DATA')
                    #damping
                    damp_row = layout.row(align=True)
                    damping_box = damp_row.box()
                    damping_box.label(text = "Animation Amplitude Modifier:",icon='FORCE_HARMONIC')

                    #offset
                    offset_row = layout.row()
                    offset_box = offset_row.box()
                    offset_box.label(text = "Animation Angular Offset:",icon = 'ORIENTATION_GIMBAL')
        
                    if active_bone is not None: 
                        col = damping_box.column(align=True)
                        col.prop(active_bone, "damping_x_scale",toggle=True, expand=True)
                        col.prop(active_bone, "damping_y_scale",toggle=True, expand=True)
                        col.prop(active_bone, "damping_z_scale",toggle=True, expand=True)

                        col2 = offset_box.column(align=True)
                        col2.prop(active_bone, "angular_offset_x",toggle=True, expand=True)
                        col2.prop(active_bone, "angular_offset_y",toggle=True, expand=True)
                        col2.prop(active_bone, "angular_offset_z",toggle=True, expand=True)
                    else: 
                        infor_messsage = layout.row()
                        infor_messsage.label(text= "select a bone")
            else: 
                box_warn = self.layout.box()
                box_warn.label(text='Select the ARMATURE and go to POSEMODE', icon="OUTLINER_OB_LIGHT")   

        else:
            box_warn = self.layout.box()
            box_warn.label(text='Select an ARMATURE with animation', icon="OUTLINER_OB_LIGHT")

 
            


classes = (VIEW3D_PT_cafpmainpanle,BoneAnimatorOffDamp)

def register():
    for clas in classes:
        register_class(clas)

def unregister():
    for clas in reversed(classes):
        unregister_class(clas)
