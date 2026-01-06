import speedtest
import time
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

import os

from config import config

logger = logging.getLogger(__name__)

class SpeedTester:
    """Handles internet speed testing with retry logic"""
    
    def __init__(self):
        self.st = speedtest.Speedtest()
        self.st.get_best_server()
    
    def run_test(self, max_retries: int = None) -> Optional[Dict]:
        """
        Run speed test with retry logic
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with test results or None if all retries fail
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES
            
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Running speed test (attempt {attempt + 1}/{max_retries + 1})")

                # Get server info
                server = self.st.get_best_server()
                
                # Run tests
                download_speed = self.st.download() / 1_000_000  # Convert to Mbps
                upload_speed = self.st.upload() / 1_000_000      # Convert to Mbps
                ping = self.st.results.ping
                
                results = {
                    'timestamp': datetime.now().isoformat(),
                    'download_mbps': round(download_speed, 2),
                    'upload_mbps': round(upload_speed, 2),
                    'ping_ms': round(ping, 2),
                    'server_name': server['name'],
                    'server_country': server['country'],
                    'attempts': attempt + 1,
                    'success': True
                }
                
                logger.info(f"Test successful: {results['download_mbps']} Mbps down, "
                          f"{results['upload_mbps']} Mbps up")
                return results
                
            except Exception as e:
                logger.warning(f"Speed test attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries:
                    time.sleep(config.RETRY_DELAY_SECONDS)
                    continue
                else:
                    logger.error(f"All {max_retries + 1} attempts failed")
                    return {
                        'timestamp': datetime.now().isoformat(),
                        'download_mbps': 0.0,
                        'upload_mbps': 0.0,
                        'ping_ms': 0.0,
                        'server_name': 'Failed',
                        'server_country': 'Failed',
                        'attempts': attempt + 1,
                        'success': False,
                        'error': str(e)
                    }
    
    def get_single_test(self) -> Optional[Dict]:
        """Run a single speed test without retries (for manual testing)"""
        return self.run_test(max_retries=0)