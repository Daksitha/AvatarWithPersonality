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
    "version" : (0, 1, 2),
    "location" : "View3D",
    "warning" : "",
    "category" : "Animation"
}

import bpy 
from bpy.utils import unregister_class
from bpy.utils import register_class
import os
import json
from bpy.app.handlers import save_post

#from . damping_tools import DampAnimation
#from . offset_tools import AngularOffsetAnimation
from . bone_motion import BoneAnimatorOffDamp
from . time_warping import CreateTimeWarpingCurve
from . time_warping import TimeWarper

from . file_op import ExportPoseBone
from . file_op import LoadPoseBone

import CAfP.global_config as global_config

from . import file_op
from . import bone_motion

from bpy.app.handlers import persistent
################# Globals #############

# @persistent    
# def change_param_file_name(scene):
#     blender_path =bpy.data.filepath
#     blen_file_name = file_op.simple_path(blender_path)
#     global_config.BONE_PARAMETERS_FILE_NAME = blen_file_name

# bpy.app.handlers.save_post.append(change_param_file_name)
################## bone properties ###################
def update_bone_animation(self, context):
    #print("bone animator", self)
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

## animation range 
#start
bpy.types.PoseBone.anim_start = bpy.props.IntProperty(
        name = "Anim_start_kf",
        description="Starting keyframe from where the animation changes will affect",
        default=0, 
    
    )

#how many kf to ignore from the start
bpy.types.PoseBone.anim_ignore_from_start = bpy.props.IntProperty(
        name = "Ignore_from_start(kf)",
        description="How many kf to ignore from the start",
        default=0, 
      
    )

#how many kf to ignore from the end
bpy.types.PoseBone.anim_ignore_from_end = bpy.props.IntProperty(
        name = "Ignore_from_end(kf)",
        description="How many kf to ignore from the end",
        default=0, 
        
    )

#range selected flag 
bpy.types.PoseBone.is_range_selected = bpy.props.BoolProperty(
        name = "isRangeSelected",
        description="check whethere the range to be edited is selected",
        default=False, 
        
    )


#################  NLA Opporation variable ##################
nla_strip_list = []
def get_nla_strips_list(scene, context):
    global nla_strip_list
    nla_strip_list.clear()
    obj = context.active_object
    if obj is not None:
        if obj.animation_data is not None:
            nla_strip = obj.animation_data.nla_tracks
            if len(nla_strip):
                nla_strip = obj.animation_data.nla_tracks["NlaTrack"].strips
                for nla in nla_strip:
                    nla_strip_list.append((str(nla.name), str(nla.name), ""))
            else: 
                nla_strip_list.append(('NONE', "Select", ""))
    return nla_strip_list

# def getAnimationMax(scene,context):
#     obj = context.active_object
#     if obj is not None:
#         if obj.animation_data is not None:
#             nla_strip = obj.animation_data.nla_tracks
#             if len(nla_strip):
    

def update_timewarping(self,context):
    bpy.ops.cafp.timewarper()

 #properties   
bpy.types.Scene.nla_strips_active = bpy.props.EnumProperty( 
        name= "active nla strip",
        items=get_nla_strips_list
        )

 
bpy.types.Scene.nla_control_x = bpy.props.IntProperty( 
        name= "timewarp x",
        description="Strip_time Fcurve end point keyframe location x",
        default=0,
        min = 1,  
        update = update_timewarping
        
        )
bpy.types.Scene.nla_control_y = bpy.props.IntProperty( 
        name= "timewarp y",
        description="Strip_time Fcurve end point keyframe location y",
        default=0,
        min=1,
        update = update_timewarping
        )
#sting property 
bpy.types.Scene.nla_initial_y = bpy.props.StringProperty( 
        name= "initial y",
        description="Initial location of timewarping control curve",
        )
bpy.types.Scene.nla_initial_x = bpy.props.StringProperty( 
        name= "initial x",
        description="initial location of timewarping control curve",
        )




class SELECTRange(bpy.types.Operator):
    """
        Select the keyframe range to edit in the current animation.
    """
    bl_label = 'Select the keyframe range to edit'
    bl_idname = 'cafp.select_posebone_range'


    @classmethod
    def poll(cls, context):

        if not (context.mode == 'POSE'):
            return False

        obj = context.active_object  # type: bpy.types.Object
        active_bone = bpy.context.active_pose_bone # type: bpy.types.PoseBone
        if obj is not None:
            if obj.type == 'ARMATURE':
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        if active_bone is not None:
                            return True
        
        return False
    
    def execute(self,context):
        import json 
        active_armature = bpy.context.active_object
        active_bone = bpy.context.active_pose_bone # type: bpy.types.PoseBone

        if not len(global_config.BONE_PARAMETERS_JSON):
            path_ =bpy.path.abspath("//{}".format(global_config.BONE_PARAMETERS_FILE_NAME))
            global_config.BONE_PARAMETERS_JSON = bone_motion.getAllPoseBoneParameters(self,active_armature,path_)

        active_bone.is_range_selected = True

        # try:
        #     #save a file in the current directory
        #     path =bpy.path.abspath("//CAfP_Temp_BProperties.json")
        #     #print(path)
        #     out_data = {}
        #     out_data['armature_name'] = '{}'.format(obj.name)
        #     if not isInCurrDirectory('CAfP_Temp_BProperties.json'):
        #         with open(path, 'w') as out_file:
        #             json.dump(obj=out_data, fp=out_file, indent=2)
        #             self.report({'INFO'}, 'Create a CAfP temp_bone.json at {}'.format(path))

        #     active_bone.is_range_selected = True
        # except OSError as err:
        #     self.report('WARNING','Error {} while creating CAfP_temp_bone.json. Please save the blend file'.format(err))
        #     active_bone.is_range_selected =  False
        # except IOError as err:
        #     active_bone.is_range_selected = False
        #     if path != "":
        #         self.report({'WARNING'},"{},while creating {}. Please save the blend file".format(err,bpy.path.basename(path)))
        # except json.JSONDecodeError:
        #     active_bone.is_range_selected = False
        #     self.report({'WARNING'},"Errors in json file: {}".format(bpy.path.basename(path)))


        
        
        return {'FINISHED'}


class GoBackToRangeSelector(bpy.types.Operator):
    """
        Save the current changes for this range and go back to range panel.
    """
    bl_label = 'Go back to range selector panel'
    bl_idname = 'cafp.back_to_range_selection'

    @classmethod
    def poll(cls, context):

        if not (context.mode == 'POSE'):
            return False

        obj = context.active_object  # type: bpy.types.Object
        active_bone = bpy.context.active_pose_bone # type: bpy.types.PoseBone
        if obj is not None:
            if obj.type == 'ARMATURE':
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        if active_bone is not None:
                            return True

    def execute(self,context):
        import json
        import time

        active_armature = bpy.context.active_object
        path =bpy.path.abspath("//{}".format(global_config.BONE_PARAMETERS_FILE_NAME))
        if not len(global_config.BONE_PARAMETERS_JSON):
            global_config.BONE_PARAMETERS_JSON = bone_motion.getAllPoseBoneParameters(self,active_armature,path)
        
       
        active_bone = bpy.context.active_pose_bone
        #bone_motion.appendBoneData(self,active_bone, path)

        active_bone.is_range_selected = False


        return {'FINISHED'}
   
class ApplyBoneParameters(bpy.types.Operator):
    """
        Cash/Save pose bone configurations for future use .
    """
    bl_label = 'Save PoseBone configuration'
    bl_idname = 'cafp.save_posebone_configuration'

    @classmethod
    def poll(cls, context):

        if not (context.mode == 'POSE'):
            return False

        obj = context.active_object  # type: bpy.types.Object
        active_bone = bpy.context.active_pose_bone # type: bpy.types.PoseBone
        if obj is not None:
            if obj.type == 'ARMATURE':
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        if active_bone is not None:
                            return True

    def execute(self,context):
        import json
        import time

        
        #obj = bpy.context.active_object
        #save a file in the current directory
        path =bpy.path.abspath("//{}".format(global_config.BONE_PARAMETERS_FILE_NAME))
        active_armature = bpy.context.active_object
        if not len(global_config.BONE_PARAMETERS_JSON):
            global_config.BONE_PARAMETERS_JSON = bone_motion.getAllPoseBoneParameters(self,active_armature,path)
        
        active_bone = bpy.context.active_pose_bone
        param_json = {}
        param_json,isDefaultValue = file_op.get_bone_parameters_forJson(param_json,active_bone)

        bone_motion.appendBoneData(self,active_bone, param_json,path)

        return {'FINISHED'}





##############################   main panel  ###########################################
isArmWithAnim = False
isArmWithNLA = False



class VIEW3D_PT_cafpmainpanle(bpy.types.Panel):
    bl_label = "CAfP_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # bl_context = 'objectmode'
    bl_category = "CAfP"

  

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        global isArmWithAnim
        global isArmWithNLA
        scene = context.scene

        box_info = self.layout.box()
        

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                anim_data = active_object.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    nla_strip = anim_data.nla_tracks
                    if act is not None:
                        #only place where Animation editor GUI set true
                        isArmWithAnim = True
                        isArmWithNLA = False
                        box_info.label(text='Create Armatures for Personality', icon="OUTLINER_OB_ARMATURE")
                    elif nla_strip is not None:
                        if len(nla_strip):
                            isArmWithAnim = False
                            #only place where NLA GUI set true
                            isArmWithNLA = True
                    else:
                        box_info.label(text='Active Amature has no action nor NLA', icon="ERROR")
                        isArmWithAnim = False
                        isArmWithNLA =False     
                else:
                    box_info.label(text='Active Amature has no animation', icon="ERROR")
                    isArmWithAnim = False
                    isArmWithNLA = False      
            else:
                box_info.label(text='Active object is not ARMATURE type', icon="ERROR")
                isArmWithAnim = False
                isArmWithNLA=False       
        else:
            box_info.label(text='No active object', icon="ERROR")
            isArmWithAnim = False
            isArmWithNLA = False

        
    

        if isArmWithAnim:
            if context.mode == 'POSE':

                if global_config.gui_status.startswith("ERROR"):
                    box_err = self.layout.box()

                    if global_config.gui_status == "ERROR_BONE_OPP":
                        box_err.label(text=global_config.gui_err_msg, icon="ERROR")
                        err_locat= box_err.row()
                        err_locat.label(text="Error occured in bone operation")
                        bck_button= box_err.row()                        
                        bck_button.operator(BoneAnimatorOffDamp.bl_idname, text="back")
                    else:
                        box_err.label(text=global_config.gui_err_msg, icon="ERROR")
                        err_locat= box_err.row()
                        err_locat.label(text="Uncknown error: contact CAfP support")

                
                if global_config.gui_status.startswith("ACTIVE"):
                    active_bone = bpy.context.active_pose_bone
                    layout.row()
                    #active_armature = context.active_object
                    #layout.row().label(text="Active Bone: {}".format(bone_name), icon= 'BONE_DATA')

                    
                    


                   
                    #go back to range selector
                        
            
                    if active_bone is not None: 

                        if active_bone.is_range_selected:
                            #damping
                            damp_row = layout.row(align=True)
                            damping_box = damp_row.box()
                            damping_box.label(text = "Animation Amplitude Modifier:",icon='FORCE_HARMONIC')

                            #offset
                            offset_row = layout.row()
                            offset_box = offset_row.box()
                            offset_box.label(text = "Animation Angular Offset:",icon = 'ORIENTATION_GIMBAL')

                            col = damping_box.column(align=True)
                            col.prop(active_bone, "damping_x_scale",toggle=True, expand=True)
                            col.prop(active_bone, "damping_y_scale",toggle=True, expand=True)
                            col.prop(active_bone, "damping_z_scale",toggle=True, expand=True)

                            col2 = offset_box.column(align=True)
                            col2.prop(active_bone, "angular_offset_x",toggle=True, expand=True)
                            col2.prop(active_bone, "angular_offset_y",toggle=True, expand=True)
                            col2.prop(active_bone, "angular_offset_z",toggle=True, expand=True)

                            col3 = offset_box.row(align=True)
                            col3.operator('cafp.save_posebone_configuration', text= 'Save')
                            col3.operator('cafp.back_to_range_selection', text= 'Back')
                        else:
                            #Range 
                            settings_row = layout.row(align=True)
                            settings_box = settings_row.box()
                            settings_box.label(text="Keyframe Range for Change", icon='SETTINGS')

                            set_col = settings_box.column(align=True)
                            bn_name = set_col.row()
                            bn_name.label(text='Active Bone: {}'.format(active_bone.basename))
                            #set_col.prop(active_bone, "anim_start", expand=True)
                            set_col.prop(active_bone, "anim_ignore_from_start", expand=True)
                            set_col.prop(active_bone, "anim_ignore_from_end", expand=True)    

                            set_col.operator('cafp.select_posebone_range', text= 'Next')
                        
                    else: 
                        warning_ = layout.row(align=True)
                        warning_box = warning_.box()
                        warning_box.label(text="WARNING", icon='BONE_DATA')
                        warning_box.row().label(text="Select single bonea")

                       

                    #expoert and import 
                    exp_rw = layout.row(align=True)
                    exp_box = exp_rw.box()
                    exp_box.label(text="Load PoseBone Values", icon='EXPORT')
                    #export_butt_rw = exp_box.row()
                    #export_butt_rw.operator('cafp.export_posebone_data',text='Export')
                    import_butt_rw = exp_box.row()
                    import_butt_rw.operator('cafp.import_posebone_data',text='Import')
                    
                    #nla timewarp
                    tw_row = layout.row(align=True)
                    tw_box = tw_row.box()
                    tw_box.label(text = "Finalize the animation for timewarping:",icon='FREEZE')
                    tw_opo_row = tw_box.row()
                    tw_opo_row.operator('cafp.timewarpinggraph', text='Finalize')

            else: 
                box_warn = self.layout.box()
                box_warn.label(text='Select the ARMATURE and go to POSEMODE', icon="OUTLINER_OB_LIGHT")   
        
        #TODO: implement a funtion to delete NLA strip and get back to the animation
        if isArmWithNLA:
             #NLA panel
            tw_row = layout.row()
            tw_box = tw_row.box()
            tw_box.label(text = "Timewarpping:",icon = 'SORTTIME')

            tw_col = tw_box.column(align=True)
            tw_col.prop(scene,'nla_strips_active')

            if scene.nla_strips_active != "NONE":
                tw_info = tw_col.column(align=True)
                tw_info.label(text="Initial x and y")
                tw_info.label(text=scene.nla_initial_x)
                tw_info.label(text=scene.nla_initial_y)

                tw_col2= tw_box.column(align=True)
                #tw_col2.prop(scene,'nla_initial_x',toggle=True, expand=True)
                #tw_col2.prop(scene,'nla_initial_y',toggle=True, expand=True)

                tw_col2.prop(scene,'nla_control_x',toggle=True, expand=True)
                tw_col2.prop(scene,'nla_control_y',toggle=True, expand=True)
        
        if not isArmWithNLA and not isArmWithAnim:
            box_warn = self.layout.box()
            box_warn.label(text='Select an ARMATURE with animation_data (action or NLA)', icon="OUTLINER_OB_LIGHT")

       






 
            


classes = (VIEW3D_PT_cafpmainpanle,BoneAnimatorOffDamp,CreateTimeWarpingCurve,TimeWarper,ExportPoseBone,\
    LoadPoseBone,SELECTRange,GoBackToRangeSelector,ApplyBoneParameters)

def register():
    for clas in classes:
        register_class(clas)

def unregister():
    for clas in reversed(classes):
        unregister_class(clas)
