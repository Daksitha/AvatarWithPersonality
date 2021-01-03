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
from . time_warping import CreateTimeWarpingCurve
from . time_warping import TimeWarper
 
import CAfP.global_config as global_config

################## animation bone properties ###################
def update_bone_animation(self, context):
    print("bone animator", self)
    bpy.ops.cafp.boneanimator()
    

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
#################  NLA Opporation variable ##################
nla_strip_list = []
def get_nla_strips_list(scene, context):
    global nla_strip_list
    nla_strip_list.clear()
    obj = context.active_object
    if obj is not None:
        nla_strip = obj.animation_data.nla_tracks
        if len(nla_strip):
            nla_strip = obj.animation_data.nla_tracks["NlaTrack"].strips
            for nla in nla_strip:
                nla_strip_list.append((str(nla.name), str(nla.name), ""))
        else: 
            nla_strip_list.append(('NONE', "Select", ""))
           
    return nla_strip_list

def update_timewarping(self,context):
    bpy.ops.cafp.timewarper()
bpy.types.Scene.nla_strips_active = bpy.props.EnumProperty( 
        name= "active nla strip",
        items=get_nla_strips_list
        )

 
bpy.types.Scene.nla_control_x = bpy.props.IntProperty( 
        name= "timewarp x",
        description="Strip_time Fcurve end point keyframe location x",
        default=0, 
        soft_min = 0, 
        update = update_timewarping
        
        )
bpy.types.Scene.nla_control_y = bpy.props.IntProperty( 
         name= "timewarp y",
        description="Strip_time Fcurve end point keyframe location y",
        default=0, 
        soft_min = 0, 
        update = update_timewarping
        )


##############################   main panel  ###########################################
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
        scene = context.scene

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
                        initial_check = False     
                else:
                    box_err = self.layout.box()
                    box_err.label(text='Amature has no animation', icon="ERROR")
                    initial_check = False      
            else:
                box_err = self.layout.box()
                box_err.label(text='Object is not ARMATURE type', icon="ERROR")
                initial_check = False       
        else:
            box_err = self.layout.box()
            box_err.label(text='No active object', icon="ERROR")
            initial_check = False

        
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
                    #TODO:Active still it has no bone selected
                    #bone_name = active_bone.basename
                    layout.row()
                    #layout.row().label(text="Active Bone: {}".format(bone_name), icon= 'BONE_DATA')
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
                        infor_damp = damping_box.row()
                        info_off = offset_box.row()
                        info_off.label(text= "select a bone")
                        infor_damp.label(text= "select a bone")

                    #nla timewarp
                    tw_row = layout.row(align=True)
                    tw_box = tw_row.box()
                    tw_box.label(text = "Finalize the animation for timewarping:",icon='FREEZE')
                    tw_opo_row = tw_box.row()
                    tw_opo_row.operator('cafp.timewarpinggraph', text='Finalize')

            else: 
                box_warn = self.layout.box()
                box_warn.label(text='Select the ARMATURE and go to POSEMODE', icon="OUTLINER_OB_LIGHT")   

        else:
            box_warn = self.layout.box()
            box_warn.label(text='Select an ARMATURE with animation', icon="OUTLINER_OB_LIGHT")

        #NLA panel
        tw_row = layout.row()
        tw_box = tw_row.box()
        tw_box.label(text = "Timewarpping:",icon = 'SORTTIME')

        tw_col = tw_box.column(align=True)
        tw_col.prop(scene,'nla_strips_active')

        if scene.nla_strips_active != "NONE":
            tw_col2= tw_box.column(align=True)
            tw_col2.prop(scene,'nla_control_x',toggle=True, expand=True)
            tw_col2.prop(scene,'nla_control_y',toggle=True, expand=True)






 
            


classes = (VIEW3D_PT_cafpmainpanle,BoneAnimatorOffDamp,CreateTimeWarpingCurve,TimeWarper)

def register():
    for clas in classes:
        register_class(clas)

def unregister():
    for clas in reversed(classes):
        unregister_class(clas)
