#!/usr/bin/env python3
"""
Simple raytracer implementation for rendering 3D scenes.
Supports spheres, lighting, shadows, and basic materials.
"""

import numpy as np
from PIL import Image
import sys


class Vec3:
    """3D vector class for positions, directions, and colors."""
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.data = np.array([x, y, z], dtype=np.float64)
    
    @property
    def x(self):
        return self.data[0]
    
    @property
    def y(self):
        return self.data[1]
    
    @property
    def z(self):
        return self.data[2]
    
    def __add__(self, other):
        result = Vec3()
        result.data = self.data + other.data
        return result
    
    def __sub__(self, other):
        result = Vec3()
        result.data = self.data - other.data
        return result
    
    def __mul__(self, scalar):
        result = Vec3()
        result.data = self.data * scalar
        return result
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        result = Vec3()
        result.data = self.data / scalar
        return result
    
    def dot(self, other):
        return np.dot(self.data, other.data)
    
    def length(self):
        return np.sqrt(self.dot(self))
    
    def normalize(self):
        return self / self.length()
    
    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"


class Ray:
    """Ray with origin and direction."""
    
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.normalize()
    
    def at(self, t):
        """Get point along ray at distance t."""
        return self.origin + self.direction * t


class Material:
    """Material properties for objects."""
    
    def __init__(self, color, ambient=0.1, diffuse=0.7, specular=0.2, shininess=32):
        self.color = color
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess


class Sphere:
    """Sphere object in 3D space."""
    
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def intersect(self, ray):
        """
        Check if ray intersects sphere and return distance.
        Returns None if no intersection.
        """
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return None
        
        t = (-b - np.sqrt(discriminant)) / (2.0 * a)
        if t > 0.001:  # Small epsilon to avoid self-intersection
            return t
        
        return None
    
    def normal_at(self, point):
        """Get surface normal at a point."""
        return (point - self.center).normalize()


class Light:
    """Point light source."""
    
    def __init__(self, position, intensity=1.0):
        self.position = position
        self.intensity = intensity


class Camera:
    """Camera for rendering the scene."""
    
    def __init__(self, position, look_at, up, fov, aspect_ratio):
        self.position = position
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        
        # Calculate camera coordinate system
        forward = (look_at - position).normalize()
        right = Vec3()
        right.data = np.cross(forward.data, up.data)
        right = right.normalize()
        up_vec = Vec3()
        up_vec.data = np.cross(right.data, forward.data)
        up_vec = up_vec.normalize()
        
        # Calculate viewport dimensions
        viewport_height = 2.0 * np.tan(np.radians(fov) / 2.0)
        viewport_width = viewport_height * aspect_ratio
        
        self.horizontal = right * viewport_width
        self.vertical = up_vec * viewport_height
        self.lower_left = forward - self.horizontal / 2 - self.vertical / 2
    
    def get_ray(self, u, v):
        """Get ray for normalized viewport coordinates (u, v)."""
        direction = self.lower_left + self.horizontal * u + self.vertical * v
        return Ray(self.position, direction)


class Scene:
    """Scene containing objects and lights."""
    
    def __init__(self):
        self.objects = []
        self.lights = []
        self.background_color = Vec3(0.2, 0.2, 0.3)
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_light(self, light):
        self.lights.append(light)
    
    def intersect(self, ray):
        """Find closest intersection with scene objects."""
        closest_t = float('inf')
        closest_obj = None
        
        for obj in self.objects:
            t = obj.intersect(ray)
            if t is not None and t < closest_t:
                closest_t = t
                closest_obj = obj
        
        if closest_obj is None:
            return None, None
        
        return closest_t, closest_obj
    
    def is_shadowed(self, point, light):
        """Check if point is in shadow from light."""
        light_dir = (light.position - point).normalize()
        light_distance = (light.position - point).length()
        shadow_ray = Ray(point, light_dir)
        
        for obj in self.objects:
            t = obj.intersect(shadow_ray)
            if t is not None and t < light_distance:
                return True
        
        return False
    
    def shade(self, ray, hit_point, obj):
        """Calculate color at hit point using Phong shading."""
        normal = obj.normal_at(hit_point)
        material = obj.material
        
        # Ambient component
        color = material.color * material.ambient
        
        # Add contribution from each light
        for light in self.lights:
            if self.is_shadowed(hit_point, light):
                continue
            
            # Diffuse component
            light_dir = (light.position - hit_point).normalize()
            diffuse_strength = max(0, normal.dot(light_dir))
            diffuse = material.color * material.diffuse * diffuse_strength * light.intensity
            color = color + diffuse
            
            # Specular component
            view_dir = (ray.origin - hit_point).normalize()
            reflect_dir = self._reflect(-1 * light_dir, normal)
            spec_strength = max(0, view_dir.dot(reflect_dir)) ** material.shininess
            specular = Vec3(1, 1, 1) * material.specular * spec_strength * light.intensity
            color = color + specular
        
        return color
    
    def _reflect(self, direction, normal):
        """Reflect direction vector around normal."""
        return direction - normal * 2 * direction.dot(normal)
    
    def trace_ray(self, ray):
        """Trace a ray through the scene."""
        t, obj = self.intersect(ray)
        
        if obj is None:
            return self.background_color
        
        hit_point = ray.at(t)
        return self.shade(ray, hit_point, obj)


class Renderer:
    """Renderer that generates images from scenes."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def render(self, scene, camera):
        """Render scene from camera viewpoint."""
        image = np.zeros((self.height, self.width, 3))
        
        print(f"Rendering {self.width}x{self.height} image...")
        
        for j in range(self.height):
            if j % 50 == 0:
                print(f"  Progress: {100 * j / self.height:.1f}%")
            
            for i in range(self.width):
                u = i / (self.width - 1)
                v = 1.0 - (j / (self.height - 1))  # Flip y-axis
                
                ray = camera.get_ray(u, v)
                color = scene.trace_ray(ray)
                
                # Clamp color values to [0, 1]
                r = min(1.0, max(0.0, color.x))
                g = min(1.0, max(0.0, color.y))
                b = min(1.0, max(0.0, color.z))
                
                image[j, i] = [r, g, b]
        
        print("  Progress: 100.0%")
        print("Rendering complete!")
        
        return image
    
    def save_image(self, image, filename):
        """Save rendered image to file."""
        img_data = (image * 255).astype(np.uint8)
        img = Image.fromarray(img_data)
        img.save(filename)
        print(f"Image saved to {filename}")


def create_demo_scene():
    """Create a demo scene with multiple spheres."""
    scene = Scene()
    
    # Add spheres with different materials
    # Red sphere
    red_material = Material(Vec3(1.0, 0.2, 0.2), ambient=0.1, diffuse=0.7, specular=0.3, shininess=32)
    scene.add_object(Sphere(Vec3(0, 0, -5), 1.0, red_material))
    
    # Green sphere
    green_material = Material(Vec3(0.2, 1.0, 0.2), ambient=0.1, diffuse=0.7, specular=0.3, shininess=64)
    scene.add_object(Sphere(Vec3(-2.5, -0.5, -6), 0.8, green_material))
    
    # Blue sphere
    blue_material = Material(Vec3(0.2, 0.2, 1.0), ambient=0.1, diffuse=0.7, specular=0.5, shininess=128)
    scene.add_object(Sphere(Vec3(2.0, -0.3, -4), 0.7, blue_material))
    
    # Ground sphere (large sphere below)
    ground_material = Material(Vec3(0.5, 0.5, 0.5), ambient=0.2, diffuse=0.6, specular=0.1, shininess=16)
    scene.add_object(Sphere(Vec3(0, -101, -5), 100, ground_material))
    
    # Add lights
    scene.add_light(Light(Vec3(-5, 5, -2), intensity=0.8))
    scene.add_light(Light(Vec3(5, 3, -1), intensity=0.6))
    
    return scene


def main():
    """Main function to render a demo scene."""
    print("=== Simple Raytracer ===")
    print()
    
    # Set up scene
    scene = create_demo_scene()
    
    # Set up camera
    camera = Camera(
        position=Vec3(0, 0, 0),
        look_at=Vec3(0, 0, -5),
        up=Vec3(0, 1, 0),
        fov=60,
        aspect_ratio=16/9
    )
    
    # Set up renderer
    width = 800
    height = 450
    renderer = Renderer(width, height)
    
    # Render scene
    image = renderer.render(scene, camera)
    
    # Save output
    output_file = "raytraced_scene.png"
    renderer.save_image(image, output_file)
    print()
    print(f"Done! View the output at {output_file}")


if __name__ == "__main__":
    main()
