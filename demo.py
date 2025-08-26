#!/usr/bin/env python3
"""
Telemetry Overlay Demo Script

This script demonstrates the telemetry overlay functionality
without requiring actual video or FIT files.
"""

import sys
import os
import numpy as np
import cv2

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telemetry_overlay.simple_fit_parser import FitParser
from telemetry_overlay.video_overlay import VideoOverlay


def create_demo_video():
    """Create a simple demo video for testing."""
    print("Creating demo video...")
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('demo_video.mp4', fourcc, fps, (width, height))
    
    for frame_num in range(total_frames):
        # Create a simple animated background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient background
        for y in range(height):
            intensity = int(50 + (y / height) * 100)
            frame[y, :] = (intensity // 3, intensity // 2, intensity)
        
        # Add moving circle
        center_x = int(width / 2 + 100 * np.sin(frame_num * 0.1))
        center_y = int(height / 2)
        cv2.circle(frame, (center_x, center_y), 30, (255, 255, 255), -1)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_num}", (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print("Demo video created: demo_video.mp4")
    return 'demo_video.mp4'


def demonstrate_overlay():
    """Demonstrate the telemetry overlay functionality."""
    print("=== Telemetry Overlay Demo ===\n")
    
    # Create demo video
    video_path = create_demo_video()
    
    print("1. Testing FIT Parser...")
    # Test FIT parser with sample data
    fit_parser = FitParser("demo.fit")  # Dummy file path
    if fit_parser.parse():
        print("   ✓ FIT parser working")
        
        # Show sample metrics
        for t in [30, 60, 120, 180]:
            metrics = fit_parser.get_metrics_at_time(t)
            print(f"   Metrics at {t}s: HR={metrics.get('heart_rate', 'N/A')}, "
                  f"Speed={metrics.get('speed', 'N/A')}, Power={metrics.get('power', 'N/A')}")
        
        summary = fit_parser.get_summary()
        print(f"   Summary: {summary}")
    else:
        print("   ✗ FIT parser failed")
        return
    
    print("\n2. Testing Video Overlay...")
    # Test video overlay
    video_overlay = VideoOverlay(video_path)
    if video_overlay.load_video():
        print("   ✓ Video loaded successfully")
        print(f"   Video info: {video_overlay.width}x{video_overlay.height}, "
              f"{video_overlay.fps} fps, {video_overlay.total_frames} frames")
        
        # Create output with overlay
        output_path = 'demo_with_overlay.mp4'
        print(f"   Creating overlay video: {output_path}")
        
        def progress_callback(progress):
            if int(progress) % 25 == 0:
                print(f"   Progress: {progress:.0f}%")
        
        success = video_overlay.process_video_with_overlay(
            fit_parser, output_path, progress_callback
        )
        
        if success:
            print("   ✓ Overlay video created successfully!")
            print(f"   Output: {output_path}")
        else:
            print("   ✗ Overlay creation failed")
    else:
        print("   ✗ Video loading failed")
        return
    
    print("\n3. Testing Preview Frame...")
    # Test preview frame generation
    preview_frame = video_overlay.preview_frame(150, fit_parser)
    if preview_frame is not None:
        print("   ✓ Preview frame generated")
        cv2.imwrite('preview_frame.jpg', preview_frame)
        print("   Preview saved as: preview_frame.jpg")
    else:
        print("   ✗ Preview frame generation failed")
    
    # Cleanup
    video_overlay.cleanup()
    
    print("\n=== Demo Complete ===")
    print("\nFiles created:")
    print("- demo_video.mp4 (original video)")
    print("- demo_with_overlay.mp4 (video with telemetry overlay)")
    print("- preview_frame.jpg (sample frame with overlay)")
    
    print("\nThe application successfully:")
    print("✓ Parses telemetry data (mock FIT file)")
    print("✓ Loads and processes video files")
    print("✓ Creates overlay graphics with metrics")
    print("✓ Generates output video with overlays")
    print("✓ Provides preview functionality")


if __name__ == "__main__":
    try:
        demonstrate_overlay()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()