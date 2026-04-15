# models/certificate_setting.py
from ..extensions import db
from datetime import datetime

class CertificateSetting(db.Model):
    __tablename__ = 'certificate_settings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Image data as bytes
    logo_data = db.Column(db.LargeBinary, nullable=True)
    logo_mime = db.Column(db.String(100), nullable=True)   # e.g., 'image/png'
    
    logo2_data = db.Column(db.LargeBinary, nullable=True)   # NEW
    logo2_mime = db.Column(db.String(100), nullable=True)   # NEW
    
    logo3_data = db.Column(db.LargeBinary, nullable=True)   # NEW
    logo3_mime = db.Column(db.String(100), nullable=True)   # NEW
    
    # first signature 
    signature_data = db.Column(db.LargeBinary, nullable=True)
    signature_mime = db.Column(db.String(100), nullable=True)
    signature_name = db.Column(db.String(200), nullable=True)   # NEW
    
    # Second signature (new)
    signature2_data = db.Column(db.LargeBinary, nullable=True)
    signature2_mime = db.Column(db.String(100), nullable=True)
    signature2_name = db.Column(db.String(200), nullable=True)  # NEW
    
    # Text fields
    title_text = db.Column(db.String(200), default="Certificate of Completion")
    default_course_summary = db.Column(db.Text, nullable=True)
    footer_text = db.Column(db.String(300), nullable=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_instance(cls):
        instance = cls.query.first()
        if not instance:
            instance = cls()
            db.session.add(instance)
            db.session.commit()
        return instance

