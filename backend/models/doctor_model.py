from backend.extensions import db
from datetime import datetime

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Float)
    availability = db.Column(db.Text)  # JSON string for weekly schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade='all, delete-orphan')
    treatments = db.relationship('Treatment', backref='doctor', lazy=True)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience_years': self.experience_years,
            'consultation_fee': self.consultation_fee,
            'availability': json.loads(self.availability) if self.availability else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }