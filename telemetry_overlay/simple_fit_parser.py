"""
Simple FIT File Parser (Mock Implementation)

This is a simplified implementation for demonstration purposes.
In a production environment, use the fitparse library.
"""

import struct
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleFitParser:
    """Simplified FIT file parser for demonstration."""
    
    def __init__(self, fit_file_path: str):
        """Initialize with path to FIT file."""
        self.fit_file_path = fit_file_path
        self.data = None
        self.start_time = None
        self.activity_type = 'cycling'  # Default assumption
        
    def parse(self) -> bool:
        """Parse the FIT file (mock implementation with sample data)."""
        try:
            # For demonstration, create sample telemetry data
            # In real implementation, this would parse the actual FIT file
            logger.info("Creating sample telemetry data for demonstration")
            
            # Generate 5 minutes of sample data (300 seconds)
            duration = 300  # seconds
            
            records = []
            base_time = datetime.now()
            
            for i in range(0, duration, 1):  # 1-second intervals
                timestamp = base_time + timedelta(seconds=i)
                
                # Generate realistic sample data
                heart_rate = 140 + (i % 30) - 15  # Varies between 125-155
                speed = 8 + (i % 60) / 10  # Varies between 8-14 m/s for cycling
                power = 200 + (i % 40) - 20  # Varies between 180-220W
                
                record = {
                    'timestamp': timestamp,
                    'heart_rate': heart_rate,
                    'speed': speed,
                    'power': power
                }
                records.append(record)
            
            # Convert to DataFrame
            self.data = pd.DataFrame(records)
            self.start_time = self.data['timestamp'].iloc[0]
            
            # Calculate pace
            self._calculate_pace()
            
            # Detect activity type (simplified)
            self._detect_activity_type()
            
            logger.info(f"Generated {len(self.data)} sample data points")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            return False
    
    def _calculate_pace(self):
        """Calculate pace from speed data."""
        if 'speed' in self.data.columns:
            # Convert speed (m/s) to pace (min/km)
            self.data['pace'] = 1000 / (self.data['speed'] * 60)
            # Replace infinite values with NaN
            self.data['pace'] = self.data['pace'].replace([float('inf'), float('-inf')], pd.NA)
    
    def _detect_activity_type(self):
        """Detect activity type based on speed patterns."""
        if 'speed' in self.data.columns:
            avg_speed = self.data['speed'].mean()
            # Simple heuristic: cycling typically has higher speeds
            if avg_speed > 4.0:  # m/s
                self.activity_type = 'cycling'
            else:
                self.activity_type = 'running'
    
    def get_metrics_at_time(self, elapsed_seconds: float) -> Dict:
        """Get metrics at a specific time offset from start."""
        if self.data is None or self.start_time is None:
            return {}
        
        # Find closest time index
        closest_idx = min(len(self.data) - 1, max(0, int(elapsed_seconds)))
        
        if closest_idx >= len(self.data):
            return {}
        
        row = self.data.iloc[closest_idx]
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


# For backwards compatibility, use the simple parser
FitParser = SimpleFitParser