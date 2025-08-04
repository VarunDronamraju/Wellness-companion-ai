
# File 3: services/aiml-orchestration/src/llm/connection_handler.py
"""
Connection management and health checks for Ollama service.
"""

import logging
from typing import Dict, Any, Optional
import time
import threading
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class OllamaConnectionHandler:
    """Handles connection management and health monitoring for Ollama"""
    
    def __init__(self, health_check_interval: int = 30):
        self.ollama_client = OllamaClient()
        self.health_check_interval = health_check_interval
        self.is_monitoring = False
        self.health_check_thread = None
        self.connection_stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'last_check_time': None,
            'last_check_status': None,
            'uptime_start': None,
            'connection_issues': []
        }
    
    def start_health_monitoring(self) -> bool:
        """Start background health monitoring"""
        try:
            if self.is_monitoring:
                logger.warning("Health monitoring already running")
                return True
            
            self.is_monitoring = True
            self.connection_stats['uptime_start'] = time.time()
            
            self.health_check_thread = threading.Thread(
                target=self._health_check_loop,
                daemon=True
            )
            self.health_check_thread.start()
            
            logger.info(f"Started Ollama health monitoring (interval: {self.health_check_interval}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start health monitoring: {str(e)}")
            self.is_monitoring = False
            return False
    
    def stop_health_monitoring(self):
        """Stop background health monitoring"""
        self.is_monitoring = False
        if self.health_check_thread and self.health_check_thread.is_alive():
            self.health_check_thread.join(timeout=5)
        logger.info("Stopped Ollama health monitoring")
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self.is_monitoring:
            try:
                self._perform_health_check()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {str(e)}")
                time.sleep(self.health_check_interval)
    
    def _perform_health_check(self):
        """Perform a single health check"""
        check_time = time.time()
        self.connection_stats['total_checks'] += 1
        self.connection_stats['last_check_time'] = check_time
        
        try:
            # Test connection
            if self.ollama_client.connect():
                self.connection_stats['successful_checks'] += 1
                self.connection_stats['last_check_status'] = 'healthy'
                
                # Clear old connection issues if service is healthy
                if len(self.connection_stats['connection_issues']) > 10:
                    self.connection_stats['connection_issues'] = (
                        self.connection_stats['connection_issues'][-5:]
                    )
            else:
                self.connection_stats['failed_checks'] += 1
                self.connection_stats['last_check_status'] = 'unhealthy'
                
                # Record connection issue
                issue = {
                    'timestamp': check_time,
                    'type': 'connection_failed',
                    'message': 'Failed to connect to Ollama service'
                }
                self.connection_stats['connection_issues'].append(issue)
                
        except Exception as e:
            self.connection_stats['failed_checks'] += 1
            self.connection_stats['last_check_status'] = 'error'
            
            issue = {
                'timestamp': check_time,
                'type': 'health_check_exception',
                'message': str(e)
            }
            self.connection_stats['connection_issues'].append(issue)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status and statistics"""
        total_checks = self.connection_stats['total_checks']
        success_rate = (
            (self.connection_stats['successful_checks'] / max(total_checks, 1)) * 100
        )
        
        uptime = None
        if self.connection_stats['uptime_start']:
            uptime = time.time() - self.connection_stats['uptime_start']
        
        return {
            'connected': self.ollama_client.connected,
            'monitoring_active': self.is_monitoring,
            'success_rate': f"{success_rate:.2f}%",
            'uptime_seconds': uptime,
            'last_check_status': self.connection_stats['last_check_status'],
            'last_check_time': self.connection_stats['last_check_time'],
            'total_health_checks': total_checks,
            'successful_checks': self.connection_stats['successful_checks'],
            'failed_checks': self.connection_stats['failed_checks'],
            'recent_issues': self.connection_stats['connection_issues'][-3:],  # Last 3 issues
            'available_models': self.ollama_client.available_models
        }
    
    def test_model_inference(self, model_name: str) -> Dict[str, Any]:
        """Test model inference with a simple prompt"""
        try:
            test_prompt = "Hello, please respond with 'Model test successful.'"
            
            result = self.ollama_client.generate_response(
                model=model_name,
                prompt=test_prompt,
                temperature=0.1,
                max_tokens=50
            )
            
            if result['success']:
                response_text = result.get('response', '').lower()
                if 'successful' in response_text or 'test' in response_text:
                    return {
                        'success': True,
                        'model': model_name,
                        'response': result.get('response', ''),
                        'processing_time': result.get('processing_time', 0),
                        'test_passed': True
                    }
                else:
                    return {
                        'success': True,
                        'model': model_name,
                        'response': result.get('response', ''),
                        'processing_time': result.get('processing_time', 0),
                        'test_passed': False,
                        'note': 'Model responded but test pattern not detected'
                    }
            else:
                return {
                    'success': False,
                    'model': model_name,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Model inference test failed: {str(e)}")
            return {
                'success': False,
                'model': model_name,
                'error': str(e)
            }
