from backend.extensions import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)  # Format: "HH:MM"
    status = db.Column(db.String(20), default='booked')  # booked, completed, cancelled
    symptoms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Using back_populates for BOTH sides (Patient and Doctor)
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')  # CHANGED: Now using back_populates
    
    # Relationship with treatment (one-to-one)
    treatment = db.relationship(
        'Treatment', 
        backref='appointment', 
        uselist=False, 
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time,
            'status': self.status,
            'symptoms': self.symptoms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'treatment': self.treatment.to_dict() if self.treatment else None
        }