import bpy
import bmesh
from mathutils import Vector
import numpy as np
import math
import random

def point_on_sphere(radius, theta, phi):
    """
    Convert spherical coordinates to Cartesian coordinates.
    
    :param radius: Radius of the sphere
    :param theta: Polar angle (in radians)
    :param phi: Azimuthal angle (in radians)
    :return: Cartesian coordinates (x, y, z)
    """
    x = radius * math.sin(theta) * math.cos(phi)
    y = radius * math.sin(theta) * math.sin(phi)
    z = radius * math.cos(theta)
    return (x, y, z)

def is_object_inside_sphere(obj, sphere_center, sphere_radius):
    info = {"bool": True, "distance": 0.0}
    if obj.type != 'MESH':
        raise TypeError(f"Object '{obj.name}' is not a mesh object.")
    
    world_matrix = obj.matrix_world
    for vertex in obj.data.vertices:
        world_coord = world_matrix @ vertex.co
        distance = (world_coord - sphere_center).length
        
        if distance > sphere_radius:
            info["bool"] = False
            info["distance"] = distance
     
    return info

def make_camera_look_at(camera_name, target_name):
    # Get the camera and target objects by name
    camera = bpy.data.objects.get(camera_name)
    target = bpy.data.objects.get(target_name)
    
    if not camera:
        print(f"Camera '{camera_name}' not found.")
        return
    
    if not target:
        print(f"Target object '{target_name}' not found.")
        return
    
    # Create a new track to constraint
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    print(f"Camera '{camera_name}' is now looking at '{target_name}'.")


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

light_exists = any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects)
if not light_exists:
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
        point_info = {} 
        point_info["id"] = identifier
        point_info["vertices"] = (x, y, z)
        point_info["normal"] = (nx, ny, nz)
        trio_dicts.append(point_info)


    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name=str(trio_dicts[0]["id"]))
    obj = bpy.data.objects.new(name="Object", object_data=mesh)

    # Link the object to the scene
    bpy.context.collection.objects.link(obj)

    
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

    #move origin to center of mass of the surface
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # Set the origin to the center of the geometry
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    obj.location = (0,0,0)
    

    camera = bpy.data.objects.get('Camera')
    # Parameters
    radius = 20  # Radius of the sphere
    theta = random.uniform(0, math.pi)  # Polar angle, range [0, pi]
    phi = random.uniform(0, 2 * math.pi)  # Azimuthal angle, range [0, 2*pi]

    camera.location = point_on_sphere(radius, theta, phi)
    #point cam at origin
    make_camera_look_at("Camera", "Object")    
    #Render the frame
    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = "/Users/ramsddc1/Documents/TEMP/example.png"

    # Render the image
    bpy.ops.render.render(write_still=True)

