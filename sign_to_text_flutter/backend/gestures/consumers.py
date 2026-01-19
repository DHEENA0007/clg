"""
WebSocket consumers for real-time sign detection
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .sign_detector import detect_sign

logger = logging.getLogger(__name__)


class SignDetectionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time sign detection.
    Receives hand landmarks and returns detected signs.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()
        logger.info(f"WebSocket client connected: {self.channel_name}")
        
        # Send welcome message
        await self.send(json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Sign Detection WebSocket'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"WebSocket client disconnected: {self.channel_name}, code: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'detect')
            
            if message_type == 'detect':
                await self.handle_detection(data)
            elif message_type == 'ping':
                await self.send(json.dumps({'type': 'pong'}))
            else:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_detection(self, data):
        """Process sign detection request"""
        landmarks = data.get('landmarks')
        
        if not landmarks or len(landmarks) != 21:
            await self.send(json.dumps({
                'type': 'detection_result',
                'detected': False,
                'message': 'Invalid landmarks: expected 21 points'
            }))
            return
        
        # Detect sign
        result = detect_sign(landmarks)
        
        if result:
            await self.send(json.dumps({
                'type': 'detection_result',
                'detected': True,
                'sign': result.sign,
                'confidence': result.confidence,
                'hand_shape': result.hand_shape,
                'description': result.description,
                'emoji': result.emoji,
                'timestamp': data.get('timestamp')
            }))
        else:
            await self.send(json.dumps({
                'type': 'detection_result',
                'detected': False,
                'message': 'No gesture recognized'
            }))


class SessionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for session-based detection.
    Supports multiple clients viewing the same session.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group = f'session_{self.session_id}'
        
        # Join session group
        await self.channel_layer.group_add(
            self.session_group,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Client joined session: {self.session_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group,
            self.channel_name
        )
        logger.info(f"Client left session: {self.session_id}")
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'sign_detected':
                # Broadcast to all session members
                await self.channel_layer.group_send(
                    self.session_group,
                    {
                        'type': 'sign_update',
                        'sign': data.get('sign'),
                        'confidence': data.get('confidence'),
                        'sender': self.channel_name
                    }
                )
            elif message_type == 'clear':
                await self.channel_layer.group_send(
                    self.session_group,
                    {
                        'type': 'clear_session',
                        'sender': self.channel_name
                    }
                )
                
        except Exception as e:
            logger.error(f"Session WebSocket error: {e}")
    
    async def sign_update(self, event):
        """Send sign update to client"""
        await self.send(json.dumps({
            'type': 'sign_update',
            'sign': event['sign'],
            'confidence': event['confidence']
        }))
    
    async def clear_session(self, event):
        """Send clear command to client"""
        await self.send(json.dumps({
            'type': 'session_cleared'
        }))
