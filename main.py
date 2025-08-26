#!/usr/bin/env python3
"""
Telemetry Overlay Application - Main Entry Point

Usage:
    python main.py

This application allows you to overlay fitness metrics from FIT files 
onto video recordings.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telemetry_overlay.app import main

if __name__ == "__main__":
    main()