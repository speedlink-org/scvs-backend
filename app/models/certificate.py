from datetime import datetime
from ..extensions import db

class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student_first_name = db.Column(db.String(100), nullable=False)
    student_last_name = db.Column(db.String(100), nullable=False)
    student_full_name = db.Column(db.String(100), nullable=True) #new
    course_name = db.Column(db.String(255), nullable=False)
    course_summary = db.Column(db.Text, nullable=True)
    year_of_study = db.Column(db.String(20), nullable=True)

    verification_code = db.Column(db.String(50), unique=True, nullable=False)
    
    qr_code_url = db.Column(db.String(255), nullable=True)

    issued_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
