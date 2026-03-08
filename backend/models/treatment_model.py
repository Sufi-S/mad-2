from backend.extensions import db
from datetime import datetime

class Treatment(db.Model):
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.name if self.doctor else None,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'notes': self.notes,
            'next_visit_date': self.next_visit_date.isoformat() if self.next_visit_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }