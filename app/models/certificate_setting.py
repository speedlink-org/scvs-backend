# models/certificate_setting.py
from ..extensions import db
from datetime import datetime

class CertificateSetting(db.Model):
    __tablename__ = 'certificate_settings'

    id = db.Column(db.Integer, primary_key=True)
    
    # Image data as bytes
    logo_data = db.Column(db.LargeBinary, nullable=True)
    logo_mime = db.Column(db.String(100), nullable=True)   # e.g., 'image/png'
    
    signature_data = db.Column(db.LargeBinary, nullable=True)
    signature_mime = db.Column(db.String(100), nullable=True)
    
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









# # models/certificate_setting.py (or inside models.py)
# from ..extensions import db
# from datetime import datetime

# class CertificateSetting(db.Model):
#     __tablename__ = 'certificate_settings'

#     id = db.Column(db.Integer, primary_key=True)
#     logo_url = db.Column(db.String(500), nullable=True)
#     signature_url = db.Column(db.String(500), nullable=True)
#     title_text = db.Column(db.String(200), default="Certificate of Completion")
#     default_course_summary = db.Column(db.Text, nullable=True)
#     footer_text = db.Column(db.String(300), nullable=True)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     @classmethod
#     def get_instance(cls):
#         """Return the single settings row (create if missing)."""
#         instance = cls.query.first()
#         if not instance:
#             instance = cls()
#             db.session.add(instance)
#             db.session.commit()
#         return instance