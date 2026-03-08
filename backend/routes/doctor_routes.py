from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user_model import User
from backend.models.doctor_model import Doctor
from backend.models.patient_model import Patient
from backend.models.appointment_model import Appointment
from backend.models.treatment_model import Treatment
from datetime import datetime, timedelta
from functools import wraps
import json

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # FIXED: Convert string ID to int
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_doctor_profile():
    """Helper to get doctor profile from current user"""
    # FIXED: Convert string ID to int
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    return Doctor.query.filter_by(user_id=user.id).first()

@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@doctor_required
def dashboard():
    """Doctor dashboard with stats and upcoming appointments"""
    doctor = get_doctor_profile()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404
    
    today = datetime.now().date()
    week_later = today + timedelta(days=7)
    
    # Upcoming appointments
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == today
    ).all()
    
    # Total patients count
    total_patients = db.session.query(Patient).join(
        Appointment, Patient.id == Appointment.patient_id
    ).filter(Appointment.doctor_id == doctor.id).distinct().count()
    
    return jsonify({
        'doctor': doctor.to_dict(),
        'upcoming_appointments': [apt.to_dict() for apt in upcoming],
        'today_appointments': len(today_appointments),
        'total_patients': total_patients,
        'completed_appointments': Appointment.query.filter_by(doctor_id=doctor.id, status='completed').count()
    }), 200

@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required()
@doctor_required
def get_appointments():
    """Get doctor's appointments with optional filters"""
    doctor = get_doctor_profile()
    
    # Query params
    status = request.args.get('status')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    
    if status:
        query = query.filter_by(status=status)
    if date_from:
        query = query.filter(Appointment.appointment_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Appointment.appointment_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    return jsonify([apt.to_dict() for apt in appointments]), 200

@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@jwt_required()
@doctor_required
def update_appointment_status(appointment_id):
    """Update appointment status (complete/cancel)"""
    doctor = get_doctor_profile()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify doctor owns this appointment
    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    appointment.status = new_status
    db.session.commit()
    
    return jsonify({'message': f'Appointment marked as {new_status}', 'appointment': appointment.to_dict()}), 200

@doctor_bp.route('/appointments/<int:appointment_id>/treatment', methods=['POST', 'PUT'])
@jwt_required()
@doctor_required
def manage_treatment(appointment_id):
    """Add or update treatment for an appointment"""
    doctor = get_doctor_profile()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Check if treatment exists
    treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
    
    if treatment:
        # Update existing
        treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
        treatment.prescription = data.get('prescription', treatment.prescription)
        treatment.notes = data.get('notes', treatment.notes)
        if data.get('next_visit_date'):
            treatment.next_visit_date = datetime.strptime(data.get('next_visit_date'), '%Y-%m-%d').date()
    else:
        # Create new
        treatment = Treatment(
            appointment_id=appointment_id,
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes'),
            next_visit_date=datetime.strptime(data.get('next_visit_date'), '%Y-%m-%d').date() if data.get('next_visit_date') else None
        )
        db.session.add(treatment)
        
        # Update appointment status
        appointment.status = 'completed'
    
    db.session.commit()
    
    return jsonify({'message': 'Treatment saved', 'treatment': treatment.to_dict()}), 200

@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@jwt_required()
@doctor_required
def get_patient_history(patient_id):
    """Get full treatment history of a patient"""
    doctor = get_doctor_profile()
    
    # Get all treatments for this patient with this doctor
    treatments = Treatment.query.filter_by(
        patient_id=patient_id,
        doctor_id=doctor.id
    ).order_by(Treatment.created_at.desc()).all()
    
    patient = Patient.query.get_or_404(patient_id)
    
    return jsonify({
        'patient': patient.to_dict(),
        'treatments': [t.to_dict() for t in treatments]
    }), 200

@doctor_bp.route('/availability', methods=['PUT'])
@jwt_required()
@doctor_required
def update_availability():
    """Update doctor's availability for next 7 days"""
    doctor = get_doctor_profile()
    data = request.get_json()
    
    # Expected format: {"2024-01-01": ["09:00", "10:00", ...], ...}
    availability = data.get('availability', {})
    
    # Validate - only allow next 7 days
    today = datetime.now().date()
    valid_dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]
    
    for date in availability.keys():
        if date not in valid_dates:
            return jsonify({'error': f'Date {date} is outside the allowed 7-day window'}), 400
    
    doctor.availability = json.dumps(availability)
    db.session.commit()
    
    return jsonify({'message': 'Availability updated', 'availability': availability}), 200

@doctor_bp.route('/availability', methods=['GET'])
@jwt_required()
@doctor_required
def get_availability():
    """Get doctor's availability"""
    doctor = get_doctor_profile()
    return jsonify({'availability': json.loads(doctor.availability) if doctor.availability else {}}), 200