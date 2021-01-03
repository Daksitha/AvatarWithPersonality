import bpy 




class CreateTimeWarpingCurve(bpy.types.Operator):
    "Push the action to Non linear action(NLA) and create warp graph"
    bl_idname = "cafp.timewarpinggraph"
    bl_label = "timewarping graph"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls,context):
        if not (context.mode == 'POSE' or 'OBJECT'):
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

    def execute(self,context):
        obj = context.active_object
        #print("active object: {}".format(obj))
        armature_action = obj.animation_data.action
        #create a fake animation
        nlatrack = obj.animation_data.nla_tracks
        #print(len(nla_strips))
        dummy_name ="CAfP_nla_{}".format(armature_action.name)

        if len(nlatrack): 
            all_nla = obj.animation_data.nla_tracks["NlaTrack"].strips
            isNLAExist =  [nla for nla in all_nla if nla.name.startswith(dummy_name)]
        else:
            isNLAExist = False

        

        if not isNLAExist:
            self.report({'INFO'}, 'Creating a NLA Strip for {0}'.format(dummy_name))
            #copy the action
            copy_action = armature_action.copy()
            copy_action.name = dummy_name
            copy_action.use_fake_user = True
            #Creat new NLA Strip 
            track = obj.animation_data.nla_tracks.new()
            track.strips.new(copy_action.name, copy_action.frame_range[0], copy_action)
            obj.animation_data.action = None


        #creating a warp curve
        nla_strip =  obj.animation_data.nla_tracks["NlaTrack"].strips["{0}".format(dummy_name)]
        nla_strip.use_animated_time = True 
        start_time = nla_strip.action.frame_range[0]
        end_time = nla_strip.action.frame_range[1]

        #create keyframes
        nla_strip.strip_time = start_time
        nla_strip.keyframe_insert(data_path="strip_time", frame=start_time)
        nla_strip.strip_time = end_time
        nla_strip.keyframe_insert(data_path="strip_time", frame=end_time)

        return {'FINISHED'}

           
                        

class TimeWarper(bpy.types.Operator):
    "Timewarp a NLA strip"
    bl_idname = "cafp.timewarper"
    bl_label = "timewarping graph editor"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls,context):
        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            if obj.type == 'ARMATURE':
                nla_strip =  obj.animation_data.nla_tracks["NlaTrack"].strips
                if nla_strip is not None:
                    return True
        return False

    def execute(self,context):
        obj = bpy.context.active_object
        scene = context.scene

        if scene.nla_strips_active != 'NONE':
            nla_strip =  obj.animation_data.nla_tracks["NlaTrack"].strips["{0}".format(scene.nla_strips_active)]

             #fcurve
            fc = nla_strip.fcurves.find(data_path="strip_time", index=0)
            if fc is not None:
                n_keyframes = len(fc.keyframe_points)
                self.report({'INFO'}, "Length nla_strip control curve {}".format(n_keyframes))

                last_kf = fc.keyframe_points[n_keyframes-1]
                last_kf.co[0] = scene.nla_control_x
                last_kf.co[1] = scene.nla_control_y
            else: 
                self.report({'ERROR'}, "Nla strip has no time warpping curves created")
                return {'CANCELLED'}
            #update the timewarp curve
            fc.update()
            
        else: 
            self.report({'ERROR'}, "No NLA strips found in the scene")
            return {'CANCELLED'}
            


        return {'FINISHED'}

                


        


