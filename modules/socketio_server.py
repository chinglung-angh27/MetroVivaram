"""
Real-time Socket.IO server for MetroVivaram Document Management System
Handles real-time alerts and notifications between server and clients
"""
import socketio
import eventlet
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json

class MetroSocketIOServer:
    """Socket.IO server for real-time alerts and notifications"""
    
    def __init__(self, port: int = 8502):
        self.port = port
        # Create Socket.IO server with enhanced CORS configuration for Streamlit integration
        self.sio = socketio.Server(
            cors_allowed_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
            cors_credentials=True,
            async_mode='eventlet',
            logger=False,  # Reduce logging to avoid conflicts
            engineio_logger=False
        )
        
        # Wrap with WSGI app
        self.app = socketio.WSGIApp(self.sio)
        
        # Store connected clients and their info
        self.connected_clients: Dict[str, Dict] = {}
        
        # Register event handlers
        self._register_events()
        
    def _register_events(self):
        """Register all Socket.IO event handlers"""
        
        @self.sio.event
        def connect(sid, environ, auth):
            """Handle client connection"""
            print(f"Client {sid} connected")
            
            # Store client info
            self.connected_clients[sid] = {
                'connected_at': datetime.now().isoformat(),
                'user_info': auth if auth else {},
                'subscriptions': []
            }
            
            # Send welcome message
            self.sio.emit('connection_established', {
                'message': 'Connected to MetroVivaram real-time alerts',
                'timestamp': datetime.now().isoformat(),
                'client_id': sid
            }, room=sid)
            
            # Send current system status
            self._send_system_status(sid)
            
        @self.sio.event
        def disconnect(sid):
            """Handle client disconnection"""
            print(f"Client {sid} disconnected")
            if sid in self.connected_clients:
                del self.connected_clients[sid]
                
        @self.sio.event
        def subscribe_to_alerts(sid, data):
            """Subscribe client to specific alert types"""
            alert_types = data.get('alert_types', [])
            user_role = data.get('user_role', 'viewer')
            
            if sid in self.connected_clients:
                self.connected_clients[sid]['subscriptions'] = alert_types
                self.connected_clients[sid]['user_info']['role'] = user_role
                
                self.sio.emit('subscription_confirmed', {
                    'subscribed_to': alert_types,
                    'message': f'Subscribed to {len(alert_types)} alert types'
                }, room=sid)
                
        @self.sio.event
        def request_system_status(sid, data):
            """Send current system status to requesting client"""
            self._send_system_status(sid)
            
    def _send_system_status(self, sid: str):
        """Send current system status to a specific client"""
        from modules.database import DocumentDatabase
        
        try:
            db = DocumentDatabase()
            documents = db.load_data()
            
            # Get system metrics
            total_docs = len(documents)
            high_priority = len([d for d in documents if d.get('priority') == 'High'])
            recent_uploads = len([d for d in documents if d.get('upload_date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
            
            status = {
                'total_documents': total_docs,
                'high_priority_documents': high_priority,
                'uploads_today': recent_uploads,
                'connected_clients': len(self.connected_clients),
                'timestamp': datetime.now().isoformat()
            }
            
            self.sio.emit('system_status', status, room=sid)
            
        except Exception as e:
            print(f"Error sending system status: {e}")
            
    def start_server(self):
        """Start the Socket.IO server in a separate thread"""
        def run_server():
            try:
                print(f"Starting Socket.IO server on port {self.port}...")
                eventlet.wsgi.server(eventlet.listen(('localhost', self.port)), self.app)
            except Exception as e:
                print(f"Socket.IO server error: {e}")
                
        # Start server in daemon thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print(f"Socket.IO server started on http://localhost:{self.port}")
        return server_thread
        
    def emit_alert(self, alert_type: str, data: Dict, target_roles: Optional[List[str]] = None):
        """
        Emit real-time alert to connected clients
        
        Args:
            alert_type: Type of alert (document_upload, feedback_received, priority_alert, etc.)
            data: Alert data to send
            target_roles: List of user roles to send alert to (None = all clients)
        """
        alert_payload = {
            'type': alert_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'id': f"{alert_type}_{datetime.now().timestamp()}"
        }
        
        # Send to all clients or filtered by role
        if target_roles is None:
            # Send to all connected clients
            self.sio.emit('real_time_alert', alert_payload)
            print(f"Alert '{alert_type}' sent to all {len(self.connected_clients)} clients")
        else:
            # Send to specific roles only
            for sid, client_info in self.connected_clients.items():
                client_role = client_info.get('user_info', {}).get('role', 'viewer')
                if client_role in target_roles:
                    self.sio.emit('real_time_alert', alert_payload, room=sid)
            print(f"Alert '{alert_type}' sent to clients with roles: {target_roles}")
            
    def emit_document_upload_alert(self, document_data: Dict, uploader_info: Dict):
        """Emit alert for new document upload"""
        alert_data = {
            'document_id': document_data.get('id'),
            'filename': document_data.get('filename'),
            'document_type': document_data.get('document_type'),
            'priority': document_data.get('priority', 'Medium'),
            'uploader': uploader_info.get('name', 'Unknown'),
            'upload_time': document_data.get('upload_date'),
            'message': f"New {document_data.get('priority', 'Medium').lower()} priority document uploaded: {document_data.get('filename')}"
        }
        
        self.emit_alert('document_upload', alert_data)
        
    def emit_feedback_alert(self, document_id: str, feedback_data: Dict, document_name: str):
        """Emit alert for new feedback submission"""
        alert_data = {
            'document_id': document_id,
            'document_name': document_name,
            'feedback_type': feedback_data.get('type'),
            'user_name': feedback_data.get('user_name'),
            'has_text': bool(feedback_data.get('text', '').strip()),
            'message': f"New {feedback_data.get('type')} feedback received for {document_name}"
        }
        
        # Send to management roles (HR and Compliance Officer)
        self.emit_alert('feedback_received', alert_data, target_roles=['HR', 'Compliance Officer'])
        
    def emit_priority_alert(self, document_data: Dict):
        """Emit alert for high priority documents"""
        alert_data = {
            'document_id': document_data.get('id'),
            'filename': document_data.get('filename'),
            'document_type': document_data.get('document_type'),
            'uploader': document_data.get('uploaded_by'),
            'message': f"HIGH PRIORITY: {document_data.get('filename')} requires immediate attention"
        }
        
        self.emit_alert('priority_alert', alert_data)
        
    def emit_system_metric_update(self, metrics: Dict):
        """Emit system metrics update"""
        self.emit_alert('system_metrics', metrics)
        
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)
        
    def get_connected_clients_info(self) -> Dict:
        """Get detailed info about connected clients"""
        return {
            'total_clients': len(self.connected_clients),
            'clients': [
                {
                    'id': sid,
                    'connected_at': info['connected_at'],
                    'user_role': info.get('user_info', {}).get('role', 'Unknown'),
                    'subscriptions': info.get('subscriptions', [])
                }
                for sid, info in self.connected_clients.items()
            ]
        }

# Global instance
socketio_server = None

def get_socketio_server(port: int = 8502) -> MetroSocketIOServer:
    """Get or create the global Socket.IO server instance"""
    global socketio_server
    if socketio_server is None:
        socketio_server = MetroSocketIOServer(port)
    return socketio_server

def start_socketio_server(port: int = 8502):
    """Start the Socket.IO server"""
    server = get_socketio_server(port)
    return server.start_server()