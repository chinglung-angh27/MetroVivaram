"""
Real-time Alert Manager for MetroVivaram Document Management System
Provides high-level interface for sending real-time alerts
"""
from typing import Dict, List, Optional
from datetime import datetime
from modules.socketio_server import get_socketio_server

class AlertManager:
    """High-level alert management for real-time notifications"""
    
    def __init__(self):
        self.socketio_server = None
        self._initialize_server()
        
    def _initialize_server(self):
        """Initialize Socket.IO server connection"""
        try:
            self.socketio_server = get_socketio_server()
        except Exception as e:
            print(f"Alert Manager: Socket.IO server not available - {e}")
            self.socketio_server = None
            
    def is_available(self) -> bool:
        """Check if real-time alerts are available"""
        return self.socketio_server is not None
        
    def send_document_upload_alert(self, document_data: Dict, uploader_info: Dict):
        """
        Send real-time alert for new document upload
        
        Args:
            document_data: Document information (id, filename, type, priority, etc.)
            uploader_info: User information (name, role, etc.)
        """
        if not self.is_available():
            return False
            
        try:
            self.socketio_server.emit_document_upload_alert(document_data, uploader_info)
            
            # Special alert for high priority documents
            if document_data.get('priority') == 'High':
                self.socketio_server.emit_priority_alert(document_data)
                
            return True
        except Exception as e:
            print(f"Error sending document upload alert: {e}")
            return False
            
    def send_feedback_alert(self, document_id: str, feedback_data: Dict, document_name: str):
        """
        Send real-time alert for new feedback submission
        
        Args:
            document_id: Document unique identifier
            feedback_data: Feedback information (type, user, text, etc.)
            document_name: Name of the document
        """
        if not self.is_available():
            return False
            
        try:
            self.socketio_server.emit_feedback_alert(document_id, feedback_data, document_name)
            return True
        except Exception as e:
            print(f"Error sending feedback alert: {e}")
            return False
            
    def send_priority_document_alert(self, document_data: Dict):
        """
        Send real-time alert for high priority documents
        
        Args:
            document_data: High priority document information
        """
        if not self.is_available():
            return False
            
        try:
            self.socketio_server.emit_priority_alert(document_data)
            return True
        except Exception as e:
            print(f"Error sending priority alert: {e}")
            return False
            
    def send_system_alert(self, alert_type: str, message: str, data: Optional[Dict] = None, target_roles: Optional[List[str]] = None):
        """
        Send custom system alert
        
        Args:
            alert_type: Type of alert (system_maintenance, security_alert, etc.)
            message: Alert message
            data: Additional data to include
            target_roles: Specific user roles to target
        """
        if not self.is_available():
            return False
            
        try:
            alert_data = {
                'message': message,
                'severity': 'info',
                'data': data or {}
            }
            
            self.socketio_server.emit_alert(alert_type, alert_data, target_roles)
            return True
        except Exception as e:
            print(f"Error sending system alert: {e}")
            return False
            
    def send_user_activity_alert(self, activity_type: str, user_info: Dict, details: Dict):
        """
        Send alert about user activities (login, upload, etc.)
        
        Args:
            activity_type: Type of activity (user_login, document_download, etc.)
            user_info: User information
            details: Activity details
        """
        if not self.is_available():
            return False
            
        try:
            alert_data = {
                'user_name': user_info.get('name', 'Unknown'),
                'user_role': user_info.get('role', 'Unknown'),
                'activity': activity_type,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to management roles only
            self.socketio_server.emit_alert('user_activity', alert_data, target_roles=['HR', 'Compliance Officer'])
            return True
        except Exception as e:
            print(f"Error sending user activity alert: {e}")
            return False
            
    def send_document_expiry_alert(self, expiring_documents: List[Dict]):
        """
        Send alert about documents expiring soon
        
        Args:
            expiring_documents: List of documents expiring within threshold
        """
        if not self.is_available() or not expiring_documents:
            return False
            
        try:
            alert_data = {
                'expiring_count': len(expiring_documents),
                'documents': [
                    {
                        'id': doc['id'],
                        'filename': doc['filename'],
                        'expiry_date': doc.get('expiry_date'),
                        'days_remaining': doc.get('days_remaining', 0)
                    }
                    for doc in expiring_documents[:5]  # Limit to first 5
                ],
                'message': f"{len(expiring_documents)} document(s) expiring soon"
            }
            
            self.socketio_server.emit_alert('document_expiry', alert_data)
            return True
        except Exception as e:
            print(f"Error sending document expiry alert: {e}")
            return False
            
    def send_system_metrics_update(self, metrics: Dict):
        """
        Send real-time system metrics update
        
        Args:
            metrics: Current system metrics
        """
        if not self.is_available():
            return False
            
        try:
            self.socketio_server.emit_system_metric_update(metrics)
            return True
        except Exception as e:
            print(f"Error sending metrics update: {e}")
            return False
            
    def get_connection_info(self) -> Dict:
        """Get information about current Socket.IO connections"""
        if not self.is_available():
            return {'available': False, 'connected_clients': 0}
            
        try:
            return {
                'available': True,
                'connected_clients': self.socketio_server.get_connected_clients_count(),
                'server_port': self.socketio_server.port,
                'details': self.socketio_server.get_connected_clients_info()
            }
        except Exception as e:
            print(f"Error getting connection info: {e}")
            return {'available': False, 'error': str(e)}

# Global alert manager instance
_alert_manager = None

def get_alert_manager() -> AlertManager:
    """Get or create the global alert manager instance"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager

# Convenience functions for easy access
def send_document_upload_alert(document_data: Dict, uploader_info: Dict):
    """Send document upload alert"""
    return get_alert_manager().send_document_upload_alert(document_data, uploader_info)

def send_feedback_alert(document_id: str, feedback_data: Dict, document_name: str):
    """Send feedback alert"""
    return get_alert_manager().send_feedback_alert(document_id, feedback_data, document_name)

def send_priority_alert(document_data: Dict):
    """Send priority document alert"""
    return get_alert_manager().send_priority_document_alert(document_data)

def send_system_alert(alert_type: str, message: str, data: Optional[Dict] = None, target_roles: Optional[List[str]] = None):
    """Send system alert"""
    return get_alert_manager().send_system_alert(alert_type, message, data, target_roles)