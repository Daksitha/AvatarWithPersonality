import bpy 


from mathutils import Quaternion
from mathutils import Euler
from mathutils import Vector
import math

import CAfP.global_config as global_config


def bone_animator(self, act: bpy.types.Action, bone_name: str, damp_weights: Vector, angular_offset: Vector, tail_crop=0, head_crop=0, crop_start=0) -> None:
    """Apply damping effect to the motion
    """
    
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

    #We don't need to check for both, but I just keep it for now.  
    if(curve_w is None and curve_x is None and curve_y is None and curve_z is None and \
        base_curve_w is None and base_curve_x is None and base_curve_y is None and base_curve_z is None):

        
        global_config.gui_status = 'ERROR_BONE_OPP'
        global_config.gui_err_msg = 'Selected bone has no animation data, pick a bone with animation data'
        self.report({'ERROR'},"Selected bone has no animation data,pick a bone with animation data")
        return 
    else:
        global_config.gui_status = 'ACTIVE_SESSION'


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
        
        global_config.gui_status = 'ERROR_BONE_OPP'
        global_config.gui_err_msg = 'All Fcurves for {} must have {} equal number of keyframes'.format(armature_action.name,n_keyframes_w)
        self.report({'ERROR'}, 'All Fcurves for {} must have {} equal number of keyframes'.format(armature_action.name,n_keyframes_w))
        return 
    else:
        global_config.gui_status = 'ACTIVE_SESSION'

    #keyframe range 
    from_kf = crop_start+head_crop
    till_kf = n_keyframes_w-tail_crop
    kf_range = till_kf - from_kf

    
    #Select the range of the animation
    if(kf_range>0):
        minKeyframe = crop_start+head_crop
        maxKeyframe = n_keyframes_w - tail_crop
        #self.report({'INFO'}, "Damping effect applies to keyframes from {0} till {1}".format(minKeyframe,maxKeyframe))
    else:
        self.report({'WARNING'}, "Unexpected keyframe crop. n_keyframes {0}, crop (start_kf:{1},head_crop_kf:{2},tail_crop_kf:{3} "\
            .format(n_keyframes_w,crop_start,head_crop,tail_crop))
        minKeyframe = 0
        maxKeyframe = n_keyframes_w
        self.report({'INFO'}, "Applying to all keyframes from {} till {}".format(minKeyframe,maxKeyframe) ) 


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
            
            global_config.gui_status = 'ERROR_BONE_OPP'
            global_config.gui_err_msg = '{} keyframe missing in one of the FCurves'.format(kf_w.co[0])
            self.report({'ERROR'}, '{} keyframe missing in one of the FCurves'.format(kf_w.co[0]))
            return 
        else:
            global_config.gui_status = 'ACTIVE_SESSION'


        # Retrieve the base roation
        current_q = Quaternion((base_kf_w.co[1], base_kf_x.co[1], base_kf_y.co[1], base_kf_z.co[1]))
        current_eulr = current_q.to_euler()

        #Damp oporation 
        new_euler = Euler((x * y for x, y in zip( damp_weights,current_eulr )), 'XYZ')
        damped_quat = new_euler.to_quaternion()

        #Offset 

        quat_x = Quaternion((1.0, 0.0, 0.0), math.radians(angular_offset[0]))
        quat_y = Quaternion((0.0, 1.0, 0.0), math.radians(angular_offset[1]))
        quat_z = Quaternion((0.0, 0.0, 1.0), math.radians(angular_offset[2]))
        quat_ofset = quat_x @ quat_y @ quat_z

        #TODO: does the order matter? 
        new_qat = quat_ofset @ damped_quat
        new_qat.normalize()
        
        #update armature action
        kf_w.co[1], kf_x.co[1], kf_y.co[1], kf_z.co[1] = new_qat

    # Force timings and handles update
    curve_w.update()
    curve_x.update()
    curve_y.update()
    curve_z.update() 

def get_bone_properties(bone):
        active_bone=bone

        x_dp = active_bone.damping_x_scale
        y_dp = active_bone.damping_y_scale
        z_dp = active_bone.damping_z_scale
        damping_weights = Vector((x_dp,y_dp,z_dp))

        x_an = active_bone.angular_offset_x
        y_an = active_bone.angular_offset_y
        z_an = active_bone.angular_offset_z
        angular_offset = Vector((x_an,y_an,z_an))

        s_crop = active_bone.anim_start
        head_crop = active_bone.anim_ignore_from_start
        tail_crop = active_bone.anim_ignore_from_end
        edit_range = [s_crop,head_crop,tail_crop]
        return damping_weights,angular_offset,edit_range

class BoneAnimatorOffDamp(bpy.types.Operator):
    """Rotational translate animation curves"""
    bl_idname = "cafp.boneanimator"
    bl_label = "offset and damp Fcurve for a given animation for a a selective keyframe range"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        if not (context.mode == 'POSE'):
            return False

        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            if obj.type == 'ARMATURE':
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act is not None:
                        return True
        return False

    def execute(self, context):

        # Active Armature
        obj = context.active_object  # type: bpy.types.Object
        if obj.type != 'ARMATURE':
            self.report({'ERROR'},"Selected object {} is not ARMATURE type".format(obj))
            return {'CANCELLED'}
    
        #active item 
        active_bone = bpy.context.active_pose_bone
        #importing data to all bones selecte
        #load_data_bones= bpy.context.selected_pose_bones_from_active_object
        load_data_bones= bpy.context.visible_pose_bones
        

        #animation
        action = obj.animation_data.action

        if active_bone is not None and not global_config.IMPORT_DATA:
            bone_name = active_bone.basename

            damping_weights,angular_offset,edit_range = get_bone_properties(active_bone)
            if action is not None:
                bone_animator(self, act=action,bone_name= bone_name,damp_weights= damping_weights,\
                    angular_offset= angular_offset,tail_crop=edit_range[2], head_crop=edit_range[1], crop_start=edit_range[0])

            else:
                self.report({'ERROR'},"Armature {0} has no animation data".format(obj))
                return {'CANCELLED'}
        elif global_config.IMPORT_DATA:
            for bone_ in load_data_bones:
                bone_name = bone_.basename
                damping_weights,angular_offset,edit_range = get_bone_properties(bone_)
                bone_animator(self, act=action,bone_name= bone_name,damp_weights= damping_weights,\
                    angular_offset= angular_offset,tail_crop=edit_range[2], head_crop=edit_range[1], crop_start=edit_range[0])

        else:
            self.report({'ERROR'},"No active_bone")
            return {'CANCELLED'}

        return {'FINISHED'}
    
    
   