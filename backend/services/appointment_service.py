from extensions import db
from models.appointment_model import Appointment
from models.doctor_model import Doctor
from datetime import datetime, timedelta
import json

class AppointmentService:
    @staticmethod
    def check_availability(doctor_id, date, time):
        """Check if a time slot is available"""
        # Check if appointment exists
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            status='booked'
        ).first()
        
        if existing:
            return False, 'Slot already booked'
        
        # Check doctor's availability
        doctor = Doctor.query.get(doctor_id)
        if doctor and doctor.availability:
            availability = json.loads(doctor.availability)
            date_str = date.isoformat() if hasattr(date, 'isoformat') else date
            
            if date_str in availability:
                if time not in availability[date_str]:
                    return False, 'Doctor not available at this time'
        
        return True, 'Slot available'
    
    @staticmethod
    def get_available_slots(doctor_id, start_date=None, days=7):
        """Get available slots for a doctor for the next N days"""
        if start_date is None:
            start_date = datetime.now().date()
        
        end_date = start_date + timedelta(days=days)
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None, 'Doctor not found'
        
        # Get doctor's availability
        availability = json.loads(doctor.availability) if doctor.availability else {}
        
        # Get booked appointments
        booked = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date.between(start_date, end_date),
            Appointment.status == 'booked'
        ).all()
        
        # Build booked slots dictionary
        booked_slots = {}
        for apt in booked:
            date_str = apt.appointment_date.isoformat()
            if date_str not in booked_slots:
                booked_slots[date_str] = []
            booked_slots[date_str].append(apt.appointment_time)
        
        # Calculate available slots
        available_slots = {}
        for i in range(days + 1):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.isoformat()
            
            if date_str in availability:
                # Get all slots doctor is available
                all_slots = availability[date_str]
                # Remove booked slots
                booked = booked_slots.get(date_str, [])
                available = [slot for slot in all_slots if slot not in booked]
                
                if available:
                    available_slots[date_str] = available
        
        return available_slots, None
    
    @staticmethod
    def get_upcoming_reminders():
        """Get appointments for tomorrow for reminders"""
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        appointments = Appointment.query.filter_by(
            appointment_date=tomorrow,
            status='booked'
        ).all()
        
        reminders = []
        for apt in appointments:
            patient = apt.patient
            doctor = apt.doctor
            
            if patient and doctor:
                reminders.append({
                    'appointment_id': apt.id,
                    'patient_name': patient.name,
                    'patient_email': patient.user.email if patient.user else None,
                    'patient_phone': patient.phone,
                    'doctor_name': doctor.name,
                    'date': apt.appointment_date.isoformat(),
                    'time': apt.appointment_time
                })
        
        return reminders