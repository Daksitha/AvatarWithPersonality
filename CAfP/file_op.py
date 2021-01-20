import bpy
import time
import json
import os
from math import isclose
import CAfP.global_config as global_config
from bpy_extras.io_utils import ExportHelper, ImportHelper

def simple_path(input_path, use_basename=True, max_len=50):
    """
    Return the last part of long paths
    """
    if use_basename:
        return os.path.basename(input_path)

    if len(input_path) > max_len:
        return f"[Trunked]..{input_path[len(input_path)-max_len:]}"

    return input_path

def load_json_data(self, json_path, description=None):
        
        try:
            time1 = time.time()
            with open(json_path, "r") as j_file:
                j_database = json.load(j_file)
                if not description:
                    self.report({'INFO'},"Json database {} loaded in {} secs".format\
                                (simple_path(json_path), time.time()-time1))
                else:
                    self.report({'INFO'},"{} loaded from {} in {} secs".format\
                                (description, simple_path(json_path), time.time()-time1))
                return j_database
        except IOError:
            if simple_path(json_path) != "":
                self.report({'WARNING'},"File not found: {}".format(simple_path(json_path)))
        except json.JSONDecodeError:
            self.report({'WARNING'},"Errors in json file: {}".format(simple_path(json_path)))
        return None

class LoadPoseBone(bpy.types.Operator, ImportHelper):
    """
        Load cafp posebone properties from a JSON.
    """
    bl_label = 'Import for current model'
    bl_idname = 'cafp.import_posebone_data'
    filename_ext = ".json"
    #filter_glob = bpy.props.StringProperty(default="*.json", options={'HIDDEN'},)
    bl_description = 'Load a transformation file for the current model.'
    bl_context = 'posemode'
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            if obj.type =='ARMATURE':
                poseBones = context.selected_pose_bones_from_active_object
                if poseBones:
                    return True

        return False

    def execute(self, context):
       
        if not self.filepath.endswith(".json"):
            self.ShowMessageBox(message = "May not a valid file !")
            return {'FINISHED'}
        #--------------------
        scene_poseB = context.visible_pose_bones
        im_poseBones = load_json_data(self, self.filepath)
        #Setting the IMPORT_DATA flag 
        #global_config.IMPORT_DATA = True

        if im_poseBones is not None:
            for im_name, im_val_json in im_poseBones.items():
                #print("key {0} value{1}".format(im_name,im_val_json))
                for curr_bone in scene_poseB:
                    curr_bn = curr_bone.basename
                    im_bn = im_name

                   
                    #BUG: mixamorig start with a different character
                    if im_bn.startswith('mixamorig'):
                        split_im = im_bn.split(":",1)
                        if len(split_im)==2:
                            im_bn = split_im[1]
                            #im_rg_name = split_im[0]
                    if curr_bn.startswith('mixamorig'):
                        split_curr = curr_bn.split(":",1)
                        if len(split_curr) ==2:
                            curr_bn = split_curr[1]
                            #curr_rg_name = split_curr[0]


                    if curr_bn == im_bn:
                        for im_props, prp_value in im_val_json[0].items():
                            setattr(curr_bone,im_props,prp_value)

                            #print("Set {0}: {1} = {2}".format(curr_bone.basename,im_props,prp_value))
        #run the oporator to update the changes
        #bpy.ops.cafp.boneanimator()
        #global_config.IMPORT_DATA=False 

        return {'FINISHED'}
    
    def ShowMessageBox(self, message = "", title = "Error !", icon = 'ERROR'):

        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
#################### Export function ##################
def export_bone_parameters_toJson(param_json, bone):
     
    #param_json['anim_start'] = bone.anim_start
    param_json['anim_ignore_from_start'] = bone.anim_ignore_from_start
    param_json['anim_ignore_from_end'] = bone.anim_ignore_from_end

    x_scale = round(bone.damping_x_scale,3)
    y_scale = round(bone.damping_y_scale,3)
    z_scale = round(bone.damping_z_scale,3)
    
    param_json['damping_x_scale'] = x_scale
    param_json['damping_y_scale'] = y_scale
    param_json['damping_z_scale'] = z_scale
    

    x_offset = round(bone.angular_offset_x,3)
    y_offset =round( bone.angular_offset_y,3)
    z_offset = round(bone.angular_offset_z,3)


    param_json['angular_offset_x'] = x_offset
    param_json['angular_offset_y'] = y_offset
    param_json['angular_offset_z'] = z_offset

    return param_json


class ExportPoseBone(bpy.types.Operator):
    "Export all posebone angular offset and amplitude parameter to a json file"

    bl_idname = "cafp.export_posebone_data"
    bl_label = "Export Json"
    filename_ext = ".json"

    filepath: bpy.props.StringProperty(name="PoseBone JSON File",
                                             description="Save all posebone angular offset and amplitude parameter",
                                             subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            if obj.type =='ARMATURE':
                poseBones = context.selected_pose_bones_from_active_object
                if poseBones:
                    return True

        return False

    def execute(self, context):

     

        obj = context.active_object 
        poseBones = context.selected_pose_bones_from_active_object

        out_data = {}

        #metadeta
        out_data['rig_name'] =obj.name

        for bone in poseBones:  # type: bpy.types.PoseBone
            param_json = {}
            #range 
            param_json = export_bone_parameters_toJson(param_json, bone)

            if len(param_json) != 0: 
                self.report({'INFO'},"Exporting Posebone {0}".format(bone.basename))
                out_data['{0}'.format(bone.basename)] = []
                out_data['{0}'.format(bone.basename)].append(param_json)

            #print("Exporting: {0}, offsets[{1}, {2}, {3}], amplitude[{4}, {5}, {6}]".\
                #format(bone.basename,x_offset,y_offset,z_offset,x_scale,y_scale,z_scale))    
            

        if len(out_data) != 0:
            with open(self.filepath, 'w') as out_file:
                json.dump(obj=out_data, fp=out_file, indent=2)
        else: 
            self.report({'ERROR'}, "There are no changes to the selected bone(s)")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


      


##Credit to fabrizio 
class SetDummyUserToAllActions(bpy.types.Operator):
    """Operator to set 'F' (dummy user) to all actions"""

    bl_idname = "cafp.set_dummy_user_to_all_actions"
    bl_label = "Set 'F' (dummy user) to all actions"

    @classmethod
    def poll(cls, context):
        if not (context.mode == 'POSE' or context.mode == 'OBJECT'):
            return False

        return True

    def execute(self, context):

        import bpy

        for actions in bpy.data.actions:
            actions.use_fake_user = True

        return {'FINISHED'}