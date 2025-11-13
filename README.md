# FABuddy - Fashion and Raytracing

A fashion outfit management application with integrated raytracing rendering capabilities.

## Features

### Fashion Management
- Organized clothing items by category (tops, bottoms, shoes)
- Image-based outfit visualization

### Raytracing Renderer
A simple but functional raytracing engine that supports:
- **Geometric Primitives**: Spheres with configurable positions and sizes
- **Materials**: Phong shading model with ambient, diffuse, and specular components
- **Lighting**: Multiple point lights with shadows
- **Camera**: Configurable viewpoint with field of view control
- **Output**: PNG image generation

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Testing

Run the unit tests to verify the raytracer implementation:

```bash
python -m unittest test_raytracer.py -v
```

The test suite includes 18 tests covering:
- Vec3 operations (addition, subtraction, dot product, normalization)
- Ray generation and point calculation
- Sphere intersection and normal calculation
- Scene management and ray intersection
- Renderer image generation

## Usage

### Running the Raytracer

To render a demo scene:

```bash
python raytracer.py
```

This will generate a `raytraced_scene.png` file showing a scene with multiple colored spheres, lighting, and shadows.

### Raytracer Components

The raytracer includes the following components:

- **Vec3**: 3D vector class for positions, directions, and colors
- **Ray**: Ray representation with origin and direction
- **Material**: Material properties (color, ambient, diffuse, specular, shininess)
- **Sphere**: Sphere primitive with intersection testing
- **Light**: Point light source
- **Camera**: Camera with configurable field of view and aspect ratio
- **Scene**: Scene management with objects and lights
- **Renderer**: Image generation from scene description

### Creating Custom Scenes

You can create custom scenes by modifying the `create_demo_scene()` function or creating your own:

```python
from raytracer import *

# Create scene
scene = Scene()

# Add a red sphere
red_material = Material(Vec3(1.0, 0.2, 0.2))
scene.add_object(Sphere(Vec3(0, 0, -5), 1.0, red_material))

# Add a light
scene.add_light(Light(Vec3(5, 5, -2)))

# Set up camera
camera = Camera(
    position=Vec3(0, 0, 0),
    look_at=Vec3(0, 0, -5),
    up=Vec3(0, 1, 0),
    fov=60,
    aspect_ratio=16/9
)

# Render
renderer = Renderer(800, 450)
image = renderer.render(scene, camera)
renderer.save_image(image, "output.png")
```

## Project Structure

```
fabuddy/
├── bottoms/          # Bottom clothing images
├── tops/             # Top clothing images  
├── shoes/            # Shoe images
├── outfit/           # Outfit combination images
├── data/             # JSON data files
├── raytracer.py      # Raytracing renderer implementation
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Technical Details

The raytracer implements:

- **Ray-sphere intersection**: Analytical solution using quadratic formula
- **Phong shading model**: Ambient + diffuse + specular lighting
- **Shadow rays**: Hard shadows from point lights
- **Anti-aliasing**: Not implemented (future enhancement)
- **Reflections**: Not implemented (future enhancement)

## License

This project is provided as-is for educational and demonstration purposes.
