#!/usr/bin/env python3
"""
Command Line Interface for Telemetry Overlay

Usage:
    python cli.py <video_file> <fit_file> <output_file>

Example:
    python cli.py sample_video.mp4 sample_activity.fit output_with_overlay.mp4
"""

import sys
import os
import argparse
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telemetry_overlay.simple_fit_parser import FitParser
from telemetry_overlay.video_overlay import VideoOverlay

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Overlay telemetry data on video files')
    parser.add_argument('video_file', help='Input video file path')
    parser.add_argument('fit_file', help='Input FIT file path')
    parser.add_argument('output_file', help='Output video file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input files
    if not os.path.exists(args.video_file):
        logger.error(f"Video file not found: {args.video_file}")
        return 1
    
    if not os.path.exists(args.fit_file):
        logger.error(f"FIT file not found: {args.fit_file}")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    logger.info("Starting telemetry overlay process...")
    
    try:
        # Parse FIT file
        logger.info("Parsing FIT file...")
        fit_parser = FitParser(args.fit_file)
        if not fit_parser.parse():
            logger.error("Failed to parse FIT file")
            return 1
        
        # Display FIT file summary
        summary = fit_parser.get_summary()
        logger.info(f"FIT file summary:")
        logger.info(f"  Activity type: {summary.get('activity_type', 'Unknown')}")
        logger.info(f"  Data points: {summary.get('duration', 0)}")
        logger.info(f"  Has heart rate: {summary.get('has_heart_rate', False)}")
        logger.info(f"  Has speed: {summary.get('has_speed', False)}")
        logger.info(f"  Has power: {summary.get('has_power', False)}")
        
        # Load video
        logger.info("Loading video file...")
        video_overlay = VideoOverlay(args.video_file)
        if not video_overlay.load_video():
            logger.error("Failed to load video file")
            return 1
        
        # Display video info
        duration = video_overlay.get_video_duration()
        logger.info(f"Video info:")
        logger.info(f"  Resolution: {video_overlay.width}x{video_overlay.height}")
        logger.info(f"  Frame rate: {video_overlay.fps:.1f} fps")
        logger.info(f"  Duration: {duration:.1f} seconds")
        logger.info(f"  Total frames: {video_overlay.total_frames}")
        
        # Process video
        logger.info("Processing video with overlay...")
        
        def progress_callback(progress):
            if int(progress) % 10 == 0:  # Log every 10%
                logger.info(f"Progress: {progress:.1f}%")
        
        success = video_overlay.process_video_with_overlay(
            fit_parser, args.output_file, progress_callback
        )
        
        if success:
            logger.info(f"Video processing complete! Output saved to: {args.output_file}")
            return 0
        else:
            logger.error("Video processing failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        # Cleanup
        if 'video_overlay' in locals():
            video_overlay.cleanup()


if __name__ == "__main__":
    sys.exit(main())