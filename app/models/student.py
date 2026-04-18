from datetime import datetime
from ..extensions import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True,  default='')
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200), nullable=True)  # NEW
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    course_name = db.Column(db.String(255), nullable=False)
    year_of_study = db.Column(db.String(20), nullable=True)
    program_start_date = db.Column(db.Date, nullable=True)
    program_end_date = db.Column(db.Date, nullable=True)
    photo_url = db.Column(db.Text, nullable=True)

    # Relationship with Certificate
    certificates = db.relationship(
        'Certificate', backref='student', lazy=True, cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"
