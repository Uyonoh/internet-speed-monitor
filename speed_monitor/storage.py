import csv
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
from config import config

logger = logging.getLogger(__name__)

class DataStorage:
    """Handles data storage and retrieval in CSV format"""
    
    def __init__(self, data_file: str = None):
        self.data_file = Path(data_file or config.DATA_FILE)
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file with headers if it doesn't exist"""
        if not self.data_file.exists():
            headers = [
                'timestamp', 'download_mbps', 'upload_mbps', 'ping_ms',
                'server_name', 'server_country', 'attempts', 'success', 'error'
            ]
            self._write_csv_row(headers)
            logger.info(f"Created new data file: {self.data_file}")
    
    def _write_csv_row(self, row: List):
        """Write a row to the CSV file"""
        with open(self.data_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def save_result(self, result: Dict):
        """Save a test result to the data file"""
        row = [
            result.get('timestamp', datetime.now().isoformat()),
            result.get('download_mbps', 0.0),
            result.get('upload_mbps', 0.0),
            result.get('ping_ms', 0.0),
            result.get('server_name', 'Unknown'),
            result.get('server_country', 'Unknown'),
            result.get('attempts', 1),
            result.get('success', False),
            result.get('error', '')
        ]
        self._write_csv_row(row)
        logger.debug(f"Saved result: {result['timestamp']}")
    
    def load_data(self, limit: int = None) -> pd.DataFrame:
        """Load data from CSV into pandas DataFrame"""
        try:
            df = pd.read_csv(self.data_file)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False)
            if limit:
                df = df.head(limit)
            return df
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            return pd.DataFrame()
    
    def get_stats(self) -> Dict:
        """Calculate statistics from stored data"""
        df = self.load_data()
        if df.empty:
            return {}
        
        successful_tests = df[df['success'] == True]
        
        stats = {
            'total_tests': len(df),
            'successful_tests': len(successful_tests),
            'success_rate': round(len(successful_tests) / len(df) * 100, 1),
            'avg_download': round(successful_tests['download_mbps'].mean(), 2),
            'avg_upload': round(successful_tests['upload_mbps'].mean(), 2),
            'avg_ping': round(successful_tests['ping_ms'].mean(), 2),
            'max_download': round(successful_tests['download_mbps'].max(), 2),
            'min_download': round(successful_tests['download_mbps'].min(), 2),
            'recent_tests': len(df[df['timestamp'] > pd.Timestamp.now() - pd.Timedelta(days=1)]),
            'data_since': df['timestamp'].min().strftime('%Y-%m-%d %H:%M')
        }
        
        return stats