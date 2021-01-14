import bpy


import CAfP.global_config as global_config


class ExportPoseBone(bpy.types.Operator):
    "Export all posebone angular offset and amplitude parameter to a json file"

    bl_idname = "cafp.export_posebone_data"
    bl_label = "Export Posebone properties to data to a json file"
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

        import json
        from math import isclose

        #obj = context.active_object 
        poseBones = context.selected_pose_bones_from_active_object

        out_data = {}

        for bone in poseBones:  # type: bpy.types.PoseBone
            param_json = {}
            
            

            x_scale = bone.damping_x_scale
            y_scale = bone.damping_y_scale
            z_scale = bone.damping_z_scale
            if not (isclose(z_scale, 1.0) and isclose(y_scale,1.0) and isclose(z_scale,1.0)):
                param_json['damping_x_scale'] = x_scale
                param_json['damping_y_scale'] = y_scale
                param_json['damping_z_scale'] = z_scale
            
    
            x_offset = bone.angular_offset_x
            y_offset = bone.angular_offset_y
            z_offset = bone.angular_offset_z

            if x_offset != y_offset != z_offset != 0:
                param_json['angular_offset_x'] = x_offset
                param_json['angular_offset_y'] = y_offset
                param_json['angular_offset_z'] = z_offset

            if len(param_json) != 0: 
                self.report({'INFO'},"Exporting Posebone {0}".format(bone.basename))
                out_data['{0}'.format(bone.basename)] = []
                out_data['{0}'.format(bone.basename)].append(param_json)

            

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