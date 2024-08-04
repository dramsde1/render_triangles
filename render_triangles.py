import bpy
import math
import random
import mathutils

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

def render_object(stl_file_path: str, output_path: str, radius:float, theta: float, phi: float):
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

    #import stl
    # Import the STL file
    file_path = stl_file_path 
    bpy.ops.import_mesh.stl(filepath=file_path)

    # Optionally, you can center the imported object
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    bpy.ops.object.location_clear()
    obj = bpy.context.object

    #position camera
    camera = bpy.data.objects.get('Camera')
    # Get the bounding box dimensions of the object
    bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    bbox_center = 0.125 * sum((mathutils.Vector(corner) for corner in bbox_corners), mathutils.Vector())

    # Calculate the distance to fit the object within the cameraera’s view
    scene = bpy.context.scene
    camera_data = camera.data
    frame = camera_data.sensor_width / camera_data.lens

    max_dim = max(obj.dimensions)
    distance = max_dim / (2 * math.tan(camera_data.angle / 2))

    camera.location = point_on_sphere(radius, theta, phi)
    #point cam at origin
    make_camera_look_at("Camera", "Object")    

    #focus
    # Adjust the cameraera's focal length if necessary
    camera_data.lens = max_dim / frame * 0.5

    # Align the cameraera with the object
    camera.rotation_euler = (math.pi/2, 0, 0)
    camera.select_set(True)
    bpy.ops.object.track_set(type='TRACKTO')


    #Render the frame
    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path

    # Render the image
    bpy.ops.render.render(write_still=True)


render_object(stl_file_path="/Users/ramsddc1/Documents/TEMP/bunny-converted-ASCII.stl", output_path="/Users/ramsddc1/Documents/TEMP/example.png", radius=500, theta=random.uniform(0,math.pi), phi=random.uniform(0,2*math.pi))
