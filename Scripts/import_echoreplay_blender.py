# Imports a replay file
import bpy
import zipfile
import os
import sys
import tempfile
import json
import datetime
from mathutils import Vector
fmt = r'%Y/%m/%d %H:%M:%S.%f'

# extracts the JSON object and the timestamp from a .echoreplay line
def get_frame(line: str):
    timestamp, jsondata = line.split("\t")
    frame = json.loads(jsondata)
    frame['real_time'] = datetime.datetime.strptime(timestamp, fmt)
    return frame


# extract the .echoreplay file
def read_replay_file(filepath):
    data = []
    if zipfile.is_zipfile(filepath):
        # Unzip
        with zipfile.ZipFile(filepath, 'r') as zf:
            with tempfile.TemporaryDirectory() as td:
                zf.extractall(td)
                for entry in os.scandir(td):
                    with open(entry.path, 'r') as f:
                        data.extend(f.readlines())
    else:
        with open(filepath) as f:
            data.extend(f.readlines())

    print("Loaded file into memory ({0} lines)".format(len(data)))
    frames = [get_frame(line) for line in data if len(line) > 800]
    print("Loaded JSON frames...")
    return frames

frames = read_replay_file('C:\\Users\\Anton\\Documents\Spark\\replays\\clip_2021-08-23_19-39-25_manual.echoreplay')




frame_time = 1.0 / bpy.context.scene.render.fps
print(frame_time)


camera_data = bpy.data.cameras.new(name='Camera')
camera_data
camera_object = bpy.data.objects.new('Camera', camera_data)
bpy.context.collection.objects.link(camera_object)




player_objects = {}



last_frame_time = frames[0]['real_time']
i = 0
for frame in frames:
    
    # now we will describe frame with number i
    bpy.context.scene.frame_set(int(i))
    
    
    local_pos = (frame['player']['vr_position'][2],frame['player']['vr_position'][0],frame['player']['vr_position'][1])    
    local_forward = (frame['player']['vr_forward'][2],frame['player']['vr_forward'][0],frame['player']['vr_forward'][1])    
    local_up = (frame['player']['vr_up'][2],frame['player']['vr_up'][0],frame['player']['vr_up'][1])    
    
    disc_pos = (frame['disc']['position'][2],frame['disc']['position'][0],frame['disc']['position'][1])
    disc_forward = (frame['disc']['forward'][2],frame['disc']['forward'][0],frame['disc']['forward'][1])
    disc_up = (frame['disc']['up'][2],frame['disc']['up'][0],frame['disc']['up'][1])
    
    
    
    for team in frame['teams']:
        for player in team['players']:
            if player['name'] not in player_objects:
                # create the sphere
                bpy.ops.mesh.primitive_ico_sphere_add()
                # add it to the dict
                player_objects[player['name']] = bpy.context.active_object
                player_objects[player['name']].name = player['name']
                
            player_pos = (player['head']['position'][2],player['head']['position'][0],player['head']['position'][1])            
            player_objects[player['name']].location = player_pos
            player_objects[player['name']].keyframe_insert(data_path="location", index=-1)
    

    
    camera_object.location = local_pos
    camera_object.keyframe_insert(data_path="location", index=-1)

    camera_object.rotation_euler = Vector(local_forward).to_track_quat('-Z', 'Y').to_euler()
    camera_object.keyframe_insert(data_path="rotation_euler", index=-1)

    i += (frame['real_time'] - last_frame_time).total_seconds() / frame_time
    last_frame_time = frame['real_time']