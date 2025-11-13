#!/usr/bin/env python3
"""
Unit tests for the raytracer implementation.
"""

import unittest
import numpy as np
from raytracer import Vec3, Ray, Material, Sphere, Light, Camera, Scene, Renderer


class TestVec3(unittest.TestCase):
    """Test Vec3 class."""
    
    def test_initialization(self):
        v = Vec3(1.0, 2.0, 3.0)
        self.assertEqual(v.x, 1.0)
        self.assertEqual(v.y, 2.0)
        self.assertEqual(v.z, 3.0)
    
    def test_addition(self):
        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, 5.0, 6.0)
        v3 = v1 + v2
        self.assertAlmostEqual(v3.x, 5.0)
        self.assertAlmostEqual(v3.y, 7.0)
        self.assertAlmostEqual(v3.z, 9.0)
    
    def test_subtraction(self):
        v1 = Vec3(4.0, 5.0, 6.0)
        v2 = Vec3(1.0, 2.0, 3.0)
        v3 = v1 - v2
        self.assertAlmostEqual(v3.x, 3.0)
        self.assertAlmostEqual(v3.y, 3.0)
        self.assertAlmostEqual(v3.z, 3.0)
    
    def test_scalar_multiplication(self):
        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = v1 * 2.0
        self.assertAlmostEqual(v2.x, 2.0)
        self.assertAlmostEqual(v2.y, 4.0)
        self.assertAlmostEqual(v2.z, 6.0)
    
    def test_dot_product(self):
        v1 = Vec3(1.0, 2.0, 3.0)
        v2 = Vec3(4.0, 5.0, 6.0)
        dot = v1.dot(v2)
        self.assertAlmostEqual(dot, 32.0)
    
    def test_length(self):
        v = Vec3(3.0, 4.0, 0.0)
        self.assertAlmostEqual(v.length(), 5.0)
    
    def test_normalize(self):
        v = Vec3(3.0, 4.0, 0.0)
        n = v.normalize()
        self.assertAlmostEqual(n.length(), 1.0)
        self.assertAlmostEqual(n.x, 0.6)
        self.assertAlmostEqual(n.y, 0.8)


class TestRay(unittest.TestCase):
    """Test Ray class."""
    
    def test_initialization(self):
        origin = Vec3(0.0, 0.0, 0.0)
        direction = Vec3(0.0, 0.0, -1.0)
        ray = Ray(origin, direction)
        self.assertEqual(ray.origin.x, 0.0)
        self.assertAlmostEqual(ray.direction.length(), 1.0)
    
    def test_at(self):
        origin = Vec3(0.0, 0.0, 0.0)
        direction = Vec3(0.0, 0.0, 1.0)
        ray = Ray(origin, direction)
        point = ray.at(5.0)
        self.assertAlmostEqual(point.x, 0.0)
        self.assertAlmostEqual(point.y, 0.0)
        self.assertAlmostEqual(point.z, 5.0)


class TestSphere(unittest.TestCase):
    """Test Sphere class."""
    
    def test_intersection_hit(self):
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        ray = Ray(Vec3(0.0, 0.0, 0.0), Vec3(0.0, 0.0, -1.0))
        t = sphere.intersect(ray)
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t, 4.0, places=5)
    
    def test_intersection_miss(self):
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        ray = Ray(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0))
        t = sphere.intersect(ray)
        self.assertIsNone(t)
    
    def test_normal_at(self):
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, 0.0), 1.0, material)
        normal = sphere.normal_at(Vec3(1.0, 0.0, 0.0))
        self.assertAlmostEqual(normal.x, 1.0)
        self.assertAlmostEqual(normal.y, 0.0)
        self.assertAlmostEqual(normal.z, 0.0)


class TestScene(unittest.TestCase):
    """Test Scene class."""
    
    def test_add_object(self):
        scene = Scene()
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        scene.add_object(sphere)
        self.assertEqual(len(scene.objects), 1)
    
    def test_add_light(self):
        scene = Scene()
        light = Light(Vec3(5.0, 5.0, 0.0))
        scene.add_light(light)
        self.assertEqual(len(scene.lights), 1)
    
    def test_intersect_hit(self):
        scene = Scene()
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        scene.add_object(sphere)
        ray = Ray(Vec3(0.0, 0.0, 0.0), Vec3(0.0, 0.0, -1.0))
        t, obj = scene.intersect(ray)
        self.assertIsNotNone(obj)
        self.assertEqual(obj, sphere)
    
    def test_intersect_miss(self):
        scene = Scene()
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        scene.add_object(sphere)
        ray = Ray(Vec3(0.0, 0.0, 0.0), Vec3(1.0, 0.0, 0.0))
        t, obj = scene.intersect(ray)
        self.assertIsNone(obj)


class TestRenderer(unittest.TestCase):
    """Test Renderer class."""
    
    def test_initialization(self):
        renderer = Renderer(100, 100)
        self.assertEqual(renderer.width, 100)
        self.assertEqual(renderer.height, 100)
    
    def test_render_dimensions(self):
        scene = Scene()
        material = Material(Vec3(1.0, 0.0, 0.0))
        sphere = Sphere(Vec3(0.0, 0.0, -5.0), 1.0, material)
        scene.add_object(sphere)
        scene.add_light(Light(Vec3(5.0, 5.0, 0.0)))
        
        camera = Camera(
            position=Vec3(0, 0, 0),
            look_at=Vec3(0, 0, -5),
            up=Vec3(0, 1, 0),
            fov=60,
            aspect_ratio=1.0
        )
        
        renderer = Renderer(50, 50)
        image = renderer.render(scene, camera)
        self.assertEqual(image.shape, (50, 50, 3))


if __name__ == '__main__':
    unittest.main()
