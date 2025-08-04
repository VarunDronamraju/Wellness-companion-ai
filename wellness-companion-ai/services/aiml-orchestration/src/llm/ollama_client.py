
# File 1: services/aiml-orchestration/src/llm/ollama_client.py
"""
Ollama API client for local LLM inference.
"""

import logging
from typing import Dict, List, Any, Optional, Generator
import requests
import json
import os
import time

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.timeout = 60  # 1 minute timeout
        self.connected = False
        self.available_models = []
        
    def connect(self) -> bool:
        """Test connection to Ollama service"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                self.connected = True
                self.available_models = [model['name'] for model in response.json().get('models', [])]
                logger.info(f"Connected to Ollama at {self.base_url}")
                logger.info(f"Available models: {self.available_models}")
                return True
            else:
                logger.error(f"Ollama connection failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            self.connected = False
            return False
    
    def list_models(self) -> Dict[str, Any]:
        """List all available models"""
        try:
            if not self.connected and not self.connect():
                return {'success': False, 'error': 'Not connected to Ollama'}
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                return {
                    'success': True,
                    'models': models_data.get('models', []),
                    'model_names': [model['name'] for model in models_data.get('models', [])]
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_response(self, 
                         model: str,
                         prompt: str,
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7,
                         max_tokens: Optional[int] = None,
                         stream: bool = False) -> Dict[str, Any]:
        """
        Generate response from Ollama model
        
        Args:
            model: Model name to use
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            
        Returns:
            Generation result
        """
        try:
            if not self.connected and not self.connect():
                return {'success': False, 'error': 'Not connected to Ollama'}
            
            # Prepare request payload
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': stream,
                'options': {
                    'temperature': temperature
                }
            }
            
            if system_prompt:
                payload['system'] = system_prompt
            
            if max_tokens:
                payload['options']['num_predict'] = max_tokens
            
            start_time = time.time()
            
            if stream:
                return self._generate_streaming(payload)
            else:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processing_time = time.time() - start_time
                    
                    return {
                        'success': True,
                        'response': result.get('response', ''),
                        'model': model,
                        'processing_time': processing_time,
                        'context': result.get('context', []),
                        'total_duration': result.get('total_duration', 0),
                        'load_duration': result.get('load_duration', 0),
                        'prompt_eval_count': result.get('prompt_eval_count', 0),
                        'eval_count': result.get('eval_count', 0)
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}: {response.text}'
                    }
                    
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_streaming(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle streaming response generation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                full_response += chunk['response']
                            if chunk.get('done', False):
                                return {
                                    'success': True,
                                    'response': full_response,
                                    'model': payload['model'],
                                    'streaming': True,
                                    'context': chunk.get('context', [])
                                }
                        except json.JSONDecodeError:
                            continue
                
                return {
                    'success': True,
                    'response': full_response,
                    'model': payload['model'],
                    'streaming': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Streaming failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def chat_completion(self,
                       model: str,
                       messages: List[Dict[str, str]],
                       temperature: float = 0.7,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Chat completion with message history
        
        Args:
            model: Model name
            messages: List of message objects with 'role' and 'content'
            temperature: Response randomness
            stream: Whether to stream response
            
        Returns:
            Chat completion result
        """
        try:
            payload = {
                'model': model,
                'messages': messages,
                'stream': stream,
                'options': {
                    'temperature': temperature
                }
            }
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                return {
                    'success': True,
                    'message': result.get('message', {}),
                    'response': result.get('message', {}).get('content', ''),
                    'model': model,
                    'processing_time': processing_time,
                    'total_duration': result.get('total_duration', 0),
                    'prompt_eval_count': result.get('prompt_eval_count', 0),
                    'eval_count': result.get('eval_count', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f'Chat completion failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull/download a model"""
        try:
            payload = {'name': model_name}
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minute timeout for model download
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': f'Model {model_name} pulled successfully'}
            else:
                return {'success': False, 'error': f'Pull failed: HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Model pull failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        try:
            payload = {'name': model_name}
            
            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'info': response.json()}
            else:
                return {'success': False, 'error': f'Model info failed: HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Get model info failed: {str(e)}")
            return {'success': False, 'error': str(e)}