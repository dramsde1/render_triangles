import bpy
import bmesh
from mathutils import Vector
import numpy as np


data = np.array([
    [0, -56.8390007019043, 10.87399959564209, 0, 0, 0, -1],
    [0, -56.71500015258789, 10.107999801635742, 0, 0, 0, -1],
    [0, -62.29999923706055, 6.566999912261963, 0, 0, 0, -1],
    [1, -56.71500015258789, 10.107999801635742, 0, 0, 0, -1],
    [1, -56.67100143432617, 9.154000282287598, 0, 0, 0, -1],
    [1, -62.29999923706055, 6.566999912261963, 0, 0, 0, -1],
    [2, -56.67100143432617, 9.154000282287598, 0, 0, 0, -1],
    [2, -56.678001403808594, 8.61299991607666, 0, 0, 0, -1],
    [2, -62.29999923706055, 6.566999912261963, 0, 0, 0, -1],
    [3, -62.15700149536133, 6.364999771118164, 0, 0, 0, -1],
    [3, -62.29999923706055, 6.566999912261963, 0, 0, 0, -1],
    [3, -56.678001403808594, 8.61299991607666, 0, 0, 0, -1],
    [4, -56.75600051879883, 7.420000076293945, 0, 0, 0, -1],
    [4, -62.15700149536133, 6.364999771118164, 0, 0, 0, -1],
    [4, -56.678001403808594, 8.61299991607666, 0, 0, 0, -1],
    [5, -56.922000885009766, 6.0920000076293945, 0, 0, 0, -1],
    [5, -62.15700149536133, 6.364999771118164, 0, 0, 0, -1],
    [5, -56.75600051879883, 7.420000076293945, 0, 0, 0, -1]
])

camera_exists = any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects)
if not camera_exists:
    #Setup Camera and Lighting
    # Add a camera
    cam_data = bpy.data.cameras.new(name='Camera')
    cam = bpy.data.objects.new('Camera', cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

# Add a light source
light_data = bpy.data.lights.new(name='Light', type='POINT')
light = bpy.data.objects.new(name='Light', object_data=light_data)
bpy.context.collection.objects.link(light)
light.location = (5, -5, 10)

for i in range(0, len(data), 3):
    trio = data[i:i+3]
    # Extract vertices from the data
    trio_dicts = []
    for identifier, x, y, z, nx, ny, nz in trio:
        mesh_info = {} 
        mesh_info["id"] = identifier
        mesh_info["vertices"] = (100 * x, 100 * y, 100 * z)
        mesh_info["normal"] = (nx, ny, nz)
        trio_dicts.append(mesh_info)


    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name=str(trio_dicts[0]["id"]))
    obj = bpy.data.objects.new(name="Object", object_data=mesh)

    # Link the object to the scene
    bpy.context.collection.objects.link(obj)
    
    obj.location = (0,0,0)

    # Create the mesh from the vertices
    verts = [i["vertices"] for i in trio_dicts]
    mesh.from_pydata(verts, [], [])
    mesh.update()
    
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')

    
    
    camera = bpy.data.objects.get('Camera')
    #point cam at origin
    # Define the origin point
    origin = Vector((0.0, 0.0, 0.0))
    
    # Calculate the direction from the camera to the origin
    direction = origin - camera.location
    
    # Point the camera at the origin
    # Calculate the rotation quaternion that points the camera at the direction
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    # Apply the rotation to the camera
    camera.rotation_euler = rot_quat.to_euler()

    #Render the frame
    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = "/Users/ramsddc1/Documents/TEMP/example.png"

    # Render the image
    bpy.ops.render.render(write_still=True)

