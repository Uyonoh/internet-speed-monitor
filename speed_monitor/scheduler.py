import schedule
import time
import threading
from datetime import datetime
from typing import Callable
import logging
from config import config

logger = logging.getLogger(__name__)

class SpeedTestScheduler:
    """Manages periodic execution of speed tests"""
    
    def __init__(self, test_callback: Callable, immediate: bool = None):
        self.test_callback = test_callback
        self.immediate = immediate if immediate is not None else config.IMMEDIATE_TEST
        self.running = False
        self.thread = None
        
    def run_test_job(self):
        """Wrapper for scheduled test execution"""
        logger.info(f"Scheduled test running at {datetime.now()}")
        self.test_callback()
    
    def start(self):
        """Start the scheduler with the configured interval"""
        if self.immediate:
            logger.info("Running immediate test as configured")
            self.test_callback()
        
        # Schedule periodic tests
        schedule.every(config.TEST_INTERVAL_MINUTES).minutes.do(self.run_test_job)
        
        logger.info(f"Scheduler started. Tests will run every {config.TEST_INTERVAL_MINUTES} minutes")
        
        # Run scheduler in background thread
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        schedule.clear()
        logger.info("Scheduler stopped")