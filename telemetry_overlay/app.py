"""
Main GUI Application for Telemetry Overlay

Provides a user interface for selecting video and FIT files, 
previewing overlays, and processing videos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import logging
from typing import Optional

from .simple_fit_parser import FitParser
from .video_overlay import VideoOverlay

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TelemetryOverlayApp:
    """Main application class."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("Telemetry Overlay")
        self.root.geometry("800x600")
        
        # Application state
        self.video_path = None
        self.fit_path = None
        self.fit_parser = None
        self.video_overlay = None
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection section
        self.setup_file_selection(main_frame)
        
        # Preview section
        self.setup_preview_section(main_frame)
        
        # Processing section
        self.setup_processing_section(main_frame)
        
        # Status section
        self.setup_status_section(main_frame)
    
    def setup_file_selection(self, parent):
        """Set up file selection UI."""
        # Video file selection
        ttk.Label(parent, text="Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.video_label = ttk.Label(parent, text="No video selected", 
                                   relief="sunken", width=50)
        self.video_label.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(parent, text="Browse", 
                  command=self.select_video_file).grid(row=0, column=2, pady=5, padx=(5, 0))
        
        # FIT file selection
        ttk.Label(parent, text="FIT File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fit_label = ttk.Label(parent, text="No FIT file selected", 
                                 relief="sunken", width=50)
        self.fit_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(parent, text="Browse", 
                  command=self.select_fit_file).grid(row=1, column=2, pady=5, padx=(5, 0))
    
    def setup_preview_section(self, parent):
        """Set up preview section."""
        # Separator
        ttk.Separator(parent, orient="horizontal").grid(row=2, column=0, columnspan=3, 
                                                       sticky=(tk.W, tk.E), pady=10)
        
        # Preview label
        ttk.Label(parent, text="Preview", font=("Arial", 12, "bold")).grid(
            row=3, column=0, columnspan=3, pady=5)
        
        # File info display
        self.info_text = tk.Text(parent, height=8, width=60, state=tk.DISABLED)
        self.info_text.grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        # Scrollbar for info text
        info_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.info_text.yview)
        info_scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        # Load files button
        self.load_button = ttk.Button(parent, text="Load Files", 
                                     command=self.load_files, state=tk.DISABLED)
        self.load_button.grid(row=5, column=1, pady=10)
    
    def setup_processing_section(self, parent):
        """Set up processing section."""
        # Separator
        ttk.Separator(parent, orient="horizontal").grid(row=6, column=0, columnspan=3, 
                                                       sticky=(tk.W, tk.E), pady=10)
        
        # Processing label
        ttk.Label(parent, text="Processing", font=("Arial", 12, "bold")).grid(
            row=7, column=0, columnspan=3, pady=5)
        
        # Output file selection
        ttk.Label(parent, text="Output File:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.output_label = ttk.Label(parent, text="Choose output location", 
                                    relief="sunken", width=50)
        self.output_label.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(parent, text="Browse", 
                  command=self.select_output_file).grid(row=8, column=2, pady=5, padx=(5, 0))
        
        # Process button
        self.process_button = ttk.Button(parent, text="Process Video", 
                                       command=self.start_processing, state=tk.DISABLED)
        self.process_button.grid(row=9, column=1, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=10, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
    
    def setup_status_section(self, parent):
        """Set up status section."""
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(parent, textvariable=self.status_var)
        self.status_label.grid(row=11, column=0, columnspan=3, pady=5)
    
    def select_video_file(self):
        """Select video file."""
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.video_label.config(text=os.path.basename(file_path))
            self.check_files_ready()
    
    def select_fit_file(self):
        """Select FIT file."""
        file_path = filedialog.askopenfilename(
            title="Select FIT File",
            filetypes=[
                ("FIT files", "*.fit"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.fit_path = file_path
            self.fit_label.config(text=os.path.basename(file_path))
            self.check_files_ready()
    
    def select_output_file(self):
        """Select output file location."""
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Video As",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.output_path = file_path
            self.output_label.config(text=os.path.basename(file_path))
            self.check_processing_ready()
    
    def check_files_ready(self):
        """Check if both files are selected and enable load button."""
        if self.video_path and self.fit_path:
            self.load_button.config(state=tk.NORMAL)
        else:
            self.load_button.config(state=tk.DISABLED)
    
    def check_processing_ready(self):
        """Check if processing can begin."""
        if (hasattr(self, 'output_path') and self.output_path and 
            self.fit_parser and self.video_overlay and not self.processing):
            self.process_button.config(state=tk.NORMAL)
        else:
            self.process_button.config(state=tk.DISABLED)
    
    def load_files(self):
        """Load and analyze the selected files."""
        self.status_var.set("Loading files...")
        self.load_button.config(state=tk.DISABLED)
        
        try:
            # Load FIT file
            self.fit_parser = FitParser(self.fit_path)
            if not self.fit_parser.parse():
                messagebox.showerror("Error", "Failed to parse FIT file")
                return
            
            # Load video file
            self.video_overlay = VideoOverlay(self.video_path)
            if not self.video_overlay.load_video():
                messagebox.showerror("Error", "Failed to load video file")
                return
            
            # Display file information
            self.display_file_info()
            
            self.status_var.set("Files loaded successfully")
            self.check_processing_ready()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            self.status_var.set("Error loading files")
        finally:
            self.load_button.config(state=tk.NORMAL)
    
    def display_file_info(self):
        """Display information about loaded files."""
        info = []
        
        # Video info
        if self.video_overlay:
            duration = self.video_overlay.get_video_duration()
            info.append("VIDEO INFORMATION:")
            info.append(f"  Resolution: {self.video_overlay.width}x{self.video_overlay.height}")
            info.append(f"  Frame Rate: {self.video_overlay.fps:.1f} fps")
            info.append(f"  Duration: {duration:.1f} seconds")
            info.append(f"  Total Frames: {self.video_overlay.total_frames}")
            info.append("")
        
        # FIT info
        if self.fit_parser:
            summary = self.fit_parser.get_summary()
            info.append("FIT FILE INFORMATION:")
            info.append(f"  Activity Type: {summary.get('activity_type', 'Unknown')}")
            info.append(f"  Data Points: {summary.get('duration', 0)}")
            info.append("  Available Metrics:")
            
            if summary.get('has_heart_rate'):
                info.append("    ✓ Heart Rate")
            if summary.get('has_speed'):
                info.append("    ✓ Speed/Pace")
            if summary.get('has_power'):
                info.append("    ✓ Power")
            
            if not any([summary.get('has_heart_rate'), summary.get('has_speed'), 
                       summary.get('has_power')]):
                info.append("    No supported metrics found")
        
        # Update text widget
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info))
        self.info_text.config(state=tk.DISABLED)
    
    def start_processing(self):
        """Start video processing in a separate thread."""
        if not hasattr(self, 'output_path') or not self.output_path:
            messagebox.showerror("Error", "Please select an output file location")
            return
        
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Processing video...")
        
        # Start processing in separate thread
        processing_thread = threading.Thread(target=self.process_video)
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_video(self):
        """Process the video with telemetry overlay."""
        try:
            def progress_callback(progress):
                self.root.after(0, lambda: self.progress_var.set(progress))
                self.root.after(0, lambda: self.status_var.set(f"Processing... {progress:.1f}%"))
            
            success = self.video_overlay.process_video_with_overlay(
                self.fit_parser, self.output_path, progress_callback
            )
            
            if success:
                self.root.after(0, lambda: self.status_var.set("Processing complete!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", f"Video processed successfully!\nOutput saved to: {self.output_path}"
                ))
            else:
                self.root.after(0, lambda: self.status_var.set("Processing failed"))
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "Failed to process video"
                ))
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.root.after(0, lambda: self.status_var.set("Processing failed"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Processing failed: {str(e)}"
            ))
        
        finally:
            self.processing = False
            self.root.after(0, lambda: self.process_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, self.check_processing_ready)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = TelemetryOverlayApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()