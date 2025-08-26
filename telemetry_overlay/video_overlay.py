"""
Video Overlay Module

Handles video processing and overlaying telemetry data onto video frames.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VideoOverlay:
    """Handles video processing and metric overlays."""
    
    def __init__(self, video_path: str):
        """Initialize with video file path."""
        self.video_path = video_path
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.width = 0
        self.height = 0
        
    def load_video(self) -> bool:
        """Load video and get properties."""
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            
            if not self.cap.isOpened():
                logger.error(f"Could not open video file: {self.video_path}")
                return False
            
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Video loaded: {self.width}x{self.height}, {self.fps} fps, {self.total_frames} frames")
            return True
            
        except Exception as e:
            logger.error(f"Error loading video: {e}")
            return False
    
    def get_video_duration(self) -> float:
        """Get video duration in seconds."""
        if self.fps > 0:
            return self.total_frames / self.fps
        return 0
    
    def create_overlay_frame(self, frame: np.ndarray, metrics: Dict, frame_number: int) -> np.ndarray:
        """Create overlay on a single frame with telemetry metrics."""
        overlay_frame = frame.copy()
        
        # Define overlay area (top-left corner)
        overlay_width = 300
        overlay_height = 150
        margin = 20
        
        # Create semi-transparent background
        overlay_bg = np.zeros((overlay_height, overlay_width, 3), dtype=np.uint8)
        overlay_bg[:] = (0, 0, 0)  # Black background
        
        # Add overlay background to frame
        roi = overlay_frame[margin:margin + overlay_height, margin:margin + overlay_width]
        overlay_frame[margin:margin + overlay_height, margin:margin + overlay_width] = cv2.addWeighted(
            roi, 0.3, overlay_bg, 0.7, 0
        )
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (255, 255, 255)  # White text
        thickness = 2
        
        # Add metrics text
        y_offset = margin + 30
        line_height = 25
        
        # Time display
        time_seconds = frame_number / self.fps if self.fps > 0 else 0
        time_str = self._format_time(time_seconds)
        cv2.putText(overlay_frame, f"Time: {time_str}", (margin + 10, y_offset), 
                   font, font_scale, color, thickness)
        y_offset += line_height
        
        # Heart rate
        if 'heart_rate' in metrics:
            cv2.putText(overlay_frame, f"HR: {metrics['heart_rate']} bpm", 
                       (margin + 10, y_offset), font, font_scale, (0, 255, 255), thickness)
        y_offset += line_height
        
        # Speed or Pace
        if 'speed' in metrics:
            cv2.putText(overlay_frame, f"Speed: {metrics['speed']} km/h", 
                       (margin + 10, y_offset), font, font_scale, (255, 255, 0), thickness)
        elif 'pace' in metrics:
            cv2.putText(overlay_frame, f"Pace: {metrics['pace']} /km", 
                       (margin + 10, y_offset), font, font_scale, (255, 255, 0), thickness)
        y_offset += line_height
        
        # Power
        if 'power' in metrics:
            cv2.putText(overlay_frame, f"Power: {metrics['power']} W", 
                       (margin + 10, y_offset), font, font_scale, (255, 0, 255), thickness)
        
        return overlay_frame
    
    def _format_time(self, seconds: float) -> str:
        """Format time as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def process_video_with_overlay(self, fit_parser, output_path: str, 
                                 progress_callback=None) -> bool:
        """Process entire video with telemetry overlay."""
        if not self.cap or not self.cap.isOpened():
            logger.error("Video not loaded")
            return False
        
        try:
            # Define codec and create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps, 
                                (self.width, self.height))
            
            frame_count = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
            
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Calculate elapsed time for this frame
                elapsed_seconds = frame_count / self.fps if self.fps > 0 else 0
                
                # Get metrics for this time
                metrics = fit_parser.get_metrics_at_time(elapsed_seconds)
                
                # Create overlay frame
                overlay_frame = self.create_overlay_frame(frame, metrics, frame_count)
                
                # Write frame
                out.write(overlay_frame)
                
                frame_count += 1
                
                # Progress callback
                if progress_callback and frame_count % 30 == 0:  # Update every 30 frames
                    progress = (frame_count / self.total_frames) * 100
                    progress_callback(progress)
            
            # Release everything
            out.release()
            
            logger.info(f"Video processing complete. Output saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return False
    
    def preview_frame(self, frame_number: int, fit_parser) -> Optional[np.ndarray]:
        """Get a preview frame with overlay at specific frame number."""
        if not self.cap or not self.cap.isOpened():
            return None
        
        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            
            if not ret:
                return None
            
            # Calculate elapsed time for this frame
            elapsed_seconds = frame_number / self.fps if self.fps > 0 else 0
            
            # Get metrics for this time
            metrics = fit_parser.get_metrics_at_time(elapsed_seconds)
            
            # Create overlay frame
            overlay_frame = self.create_overlay_frame(frame, metrics, frame_number)
            
            return overlay_frame
            
        except Exception as e:
            logger.error(f"Error creating preview frame: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
            self.cap = None