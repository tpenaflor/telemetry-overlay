# Telemetry Overlay

A Python application that overlays fitness telemetry data from FIT files onto video recordings. Perfect for creating engaging workout videos with real-time metrics display.

## Features

- **Video Support**: Compatible with MP4, AVI, MOV, MKV, and WMV formats
- **FIT File Parsing**: Extracts telemetry data from Garmin and other FIT files
- **Metric Overlays**: Displays heart rate, speed, pace, and power data
- **Activity Detection**: Automatically detects cycling vs running activities
- **Real-time Preview**: Load and preview files before processing
- **Progress Tracking**: Visual progress bar during video processing

## Supported Metrics

- **Heart Rate**: Displayed in beats per minute (bpm)
- **Speed**: For cycling activities, shown in km/h
- **Pace**: For running activities, shown in min/km format
- **Power**: Displayed in watts (W)
- **Time**: Current elapsed time in the video

## Installation

### Option 1: System Packages (Recommended for Ubuntu/Debian)

1. Clone the repository:
```bash
git clone https://github.com/tpenaflor/telemetry-overlay.git
cd telemetry-overlay
```

2. Install system packages:
```bash
sudo apt update
sudo apt install python3-numpy python3-pandas python3-opencv python3-pil python3-tk
```

3. For FIT file support, install fitparse (optional, demo works without it):
```bash
pip install --user fitparse
```

### Option 2: Virtual Environment with pip

1. Clone the repository:
```bash
git clone https://github.com/tpenaflor/telemetry-overlay.git
cd telemetry-overlay
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fitparse opencv-python numpy pandas Pillow
```

## Usage

### Demo Application

To see the application in action with sample data:
```bash
python3 demo.py
```

This will create sample video files with telemetry overlays to demonstrate the functionality.

### GUI Application

Run the main application with graphical interface:
```bash
python3 main.py
```

### Command Line Interface

For batch processing or automation:
```bash
python3 cli.py <video_file> <fit_file> <output_file>

# Example:
python3 cli.py my_ride.mp4 my_ride.fit my_ride_with_overlay.mp4
```

### Steps to Create Overlay Video:

1. **Select Video File**: Click "Browse" next to "Video File" and select your video
2. **Select FIT File**: Click "Browse" next to "FIT File" and select your FIT file
3. **Load Files**: Click "Load Files" to analyze the selected files
4. **Review Information**: Check the file information to ensure metrics are available
5. **Choose Output**: Click "Browse" next to "Output File" to set where to save the result
6. **Process Video**: Click "Process Video" to create the overlay video

## File Requirements

### Video Files
- Supported formats: MP4, AVI, MOV, MKV, WMV
- Any resolution and frame rate

### FIT Files
- Standard FIT files from fitness devices (Garmin, Wahoo, etc.)
- Must contain timestamp data
- Should include at least one of: heart rate, speed, or power data

## Dependencies

- **fitparse**: For parsing FIT files
- **opencv-python**: For video processing and overlay rendering
- **numpy**: For numerical operations
- **pandas**: For data manipulation
- **Pillow**: For image processing
- **tkinter**: For GUI (included with Python)

## Technical Details

### Overlay Design
- Semi-transparent dark background for better text visibility
- Color-coded metrics:
  - Heart Rate: Yellow
  - Speed/Pace: Cyan
  - Power: Magenta
  - Time: White

### Time Synchronization
- Automatically synchronizes FIT data timestamps with video timeline
- Uses the closest available data point for each video frame
- Handles different sampling rates between video and telemetry data

### Activity Detection
- Automatically detects activity type based on speed patterns
- Cycling: Displays speed in km/h
- Running: Displays pace in min/km format
- Falls back to speed display if activity type cannot be determined

## Example Output

The overlay appears in the top-left corner of the video with:
```
Time: 05:23
HR: 142 bpm
Speed: 32.5 km/h
Power: 245 W
```

## Troubleshooting

### Common Issues

1. **"Failed to parse FIT file"**
   - Ensure the file is a valid FIT file
   - Check that the file contains record data with timestamps

2. **"Failed to load video file"**
   - Verify the video file format is supported
   - Ensure the file is not corrupted

3. **"No supported metrics found"**
   - The FIT file doesn't contain heart rate, speed, or power data
   - Try with a different FIT file from a workout with sensors

4. **Slow processing**
   - Video processing is CPU-intensive
   - Processing time depends on video length and resolution
   - Consider using lower resolution videos for faster processing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.