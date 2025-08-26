"""
FIT File Parser Module

Handles parsing of FIT files to extract telemetry data such as:
- Heart rate
- Speed
- Pace
- Power
- Timestamps
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FitParser:
    """Parser for FIT files to extract telemetry data."""
    
    def __init__(self, fit_file_path: str):
        """Initialize with path to FIT file."""
        self.fit_file_path = fit_file_path
        self.data = None
        self.start_time = None
        self.activity_type = None
        
    def parse(self) -> bool:
        """Parse the FIT file and extract relevant data."""
        try:
            from fitparse import FitFile
            
            fitfile = FitFile(self.fit_file_path)
            
            # Extract data points
            records = []
            
            for record in fitfile.get_messages('record'):
                data_point = {}
                timestamp = None
                
                for record_data in record:
                    field_name = record_data.name
                    field_value = record_data.value
                    
                    if field_name == 'timestamp':
                        timestamp = field_value
                        data_point['timestamp'] = timestamp
                    elif field_name == 'heart_rate':
                        data_point['heart_rate'] = field_value
                    elif field_name == 'speed':
                        data_point['speed'] = field_value
                    elif field_name == 'power':
                        data_point['power'] = field_value
                    elif field_name == 'distance':
                        data_point['distance'] = field_value
                
                if timestamp:
                    records.append(data_point)
            
            # Convert to DataFrame
            if records:
                self.data = pd.DataFrame(records)
                self.data = self.data.dropna(subset=['timestamp'])
                self.data = self.data.sort_values('timestamp')
                
                # Set start time
                self.start_time = self.data['timestamp'].iloc[0]
                
                # Calculate pace if we have speed and distance
                self._calculate_pace()
                
                # Detect activity type
                self._detect_activity_type()
                
                logger.info(f"Parsed {len(self.data)} data points from FIT file")
                return True
            else:
                logger.warning("No valid data points found in FIT file")
                return False
                
        except ImportError:
            logger.error("fitparse library not installed. Run: pip install fitparse")
            return False
        except Exception as e:
            logger.error(f"Error parsing FIT file: {e}")
            return False
    
    def _calculate_pace(self):
        """Calculate pace from speed data."""
        if 'speed' in self.data.columns:
            # Convert speed (m/s) to pace (min/km)
            # Pace = 1000 / (speed * 60) for min/km
            self.data['pace'] = 1000 / (self.data['speed'] * 60)
            # Replace infinite values with NaN
            self.data['pace'] = self.data['pace'].replace([float('inf'), float('-inf')], pd.NA)
    
    def _detect_activity_type(self):
        """Detect if activity is cycling or running based on speed patterns."""
        if 'speed' in self.data.columns:
            avg_speed = self.data['speed'].mean()
            max_speed = self.data['speed'].max()
            
            # Simple heuristic: cycling typically has higher speeds
            if avg_speed > 4.0 or max_speed > 15.0:  # m/s
                self.activity_type = 'cycling'
            else:
                self.activity_type = 'running'
        else:
            self.activity_type = 'unknown'
    
    def get_metrics_at_time(self, elapsed_seconds: float) -> Dict:
        """Get metrics at a specific time offset from start."""
        if self.data is None or self.start_time is None:
            return {}
        
        target_time = self.start_time + timedelta(seconds=elapsed_seconds)
        
        # Find closest timestamp
        closest_idx = (self.data['timestamp'] - target_time).abs().idxmin()
        row = self.data.loc[closest_idx]
        
        metrics = {}
        
        if pd.notna(row.get('heart_rate')):
            metrics['heart_rate'] = int(row['heart_rate'])
        
        if pd.notna(row.get('speed')):
            if self.activity_type == 'cycling':
                # Speed in km/h for cycling
                metrics['speed'] = round(row['speed'] * 3.6, 1)
            else:
                # Pace in min/km for running
                if pd.notna(row.get('pace')):
                    pace_min = int(row['pace'])
                    pace_sec = int((row['pace'] - pace_min) * 60)
                    metrics['pace'] = f"{pace_min}:{pace_sec:02d}"
        
        if pd.notna(row.get('power')):
            metrics['power'] = int(row['power'])
        
        return metrics
    
    def get_summary(self) -> Dict:
        """Get summary statistics of the parsed data."""
        if self.data is None:
            return {}
        
        summary = {
            'duration': len(self.data),
            'activity_type': self.activity_type,
            'has_heart_rate': 'heart_rate' in self.data.columns and self.data['heart_rate'].notna().any(),
            'has_speed': 'speed' in self.data.columns and self.data['speed'].notna().any(),
            'has_power': 'power' in self.data.columns and self.data['power'].notna().any(),
        }
        
        return summary