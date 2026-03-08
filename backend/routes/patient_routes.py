from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user_model import User
from backend.models.patient_model import Patient
from backend.models.doctor_model import Doctor
from backend.models.appointment_model import Appointment
from backend.models.treatment_model import Treatment
from backend.models.department_model import Department
from datetime import datetime, timedelta
from functools import wraps
import json

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def get_patient_profile():
    """Helper to get patient profile from current user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return Patient.query.filter_by(user_id=user.id).first()

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@patient_required
def dashboard():
    """Patient dashboard with departments and appointments"""
    patient = get_patient_profile()
    
    # Get all departments/specializations
    departments = Department.query.all()
    
    # Get upcoming appointments
    today = datetime.now().date()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
    
    # Get past appointments with treatments
    past = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'completed'
    ).order_by(Appointment.appointment_date.desc()).limit(10).all()
    
    return jsonify({
        'patient': patient.to_dict(),
        'departments': [dept.to_dict() for dept in departments],
        'upcoming_appointments': [apt.to_dict() for apt in upcoming],
        'past_appointments': [apt.to_dict() for apt in past]
    }), 200

@patient_bp.route('/profile', methods=['PUT'])
@jwt_required()
@patient_required
def update_profile():
    """Update patient profile"""
    patient = get_patient_profile()
    data = request.get_json()
    
    patient.name = data.get('name', patient.name)
    patient.phone = data.get('phone', patient.phone)
    if data.get('date_of_birth'):
        patient.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
    patient.gender = data.get('gender', patient.gender)
    patient.address = data.get('address', patient.address)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.emergency_contact = data.get('emergency_contact', patient.emergency_contact)
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated', 'profile': patient.to_dict()}), 200

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@patient_required
def search_doctors():
    """Search doctors by specialization or name"""
    specialization = request.args.get('specialization', '')
    name = request.args.get('name', '')
    
    query = Doctor.query
    
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    if name:
        query = query.filter(Doctor.name.ilike(f'%{name}%'))
    
    doctors = query.all()
    
    # Get availability for each doctor
    result = []
    for doctor in doctors:
        doctor_dict = doctor.to_dict()
        # Parse availability if exists
        if doctor.availability:
            doctor_dict['availability'] = json.loads(doctor.availability)
        result.append(doctor_dict)
    
    return jsonify(result), 200

@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
@patient_required
def get_doctor_availability(doctor_id):
    """Get specific doctor's availability"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Get booked appointments for this doctor
    today = datetime.now().date()
    week_later = today + timedelta(days=7)
    
    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date.between(today, week_later),
        Appointment.status == 'booked'
    ).all()
    
    # Format booked slots
    booked_slots = {}
    for apt in booked:
        date_str = apt.appointment_date.isoformat()
        if date_str not in booked_slots:
            booked_slots[date_str] = []
        booked_slots[date_str].append(apt.appointment_time)
    
    return jsonify({
        'doctor_name': doctor.name,
        'specialization': doctor.specialization,
        'availability': json.loads(doctor.availability) if doctor.availability else {},
        'booked_slots': booked_slots
    }), 200

@patient_bp.route('/appointments', methods=['POST'])
@jwt_required()
@patient_required
def book_appointment():
    """Book a new appointment"""
    patient = get_patient_profile()
    data = request.get_json()
    
    doctor_id = data.get('doctor_id')
    appointment_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    appointment_time = data.get('time')
    
    # Check if slot is available
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status='booked'
    ).first()
    
    if existing:
        return jsonify({'error': 'This time slot is already booked'}), 400
    
    # Check doctor's availability
    doctor = Doctor.query.get(doctor_id)
    if doctor.availability:
        availability = json.loads(doctor.availability)
        date_str = appointment_date.isoformat()
        if date_str in availability:
            if appointment_time not in availability[date_str]:
                return jsonify({'error': 'Doctor is not available at this time'}), 400
    
    # Create appointment
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        symptoms=data.get('symptoms', ''),
        status='booked'
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Appointment booked successfully', 'appointment': appointment.to_dict()}), 201

@patient_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@patient_required
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    patient = get_patient_profile()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify patient owns this appointment
    if appointment.patient_id != patient.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if appointment.status != 'booked':
        return jsonify({'error': 'Cannot reschedule completed or cancelled appointments'}), 400
    
    data = request.get_json()
    new_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    new_time = data.get('time')
    
    # Check if new slot is available
    existing = Appointment.query.filter_by(
        doctor_id=appointment.doctor_id,
        appointment_date=new_date,
        appointment_time=new_time,
        status='booked'
    ).first()
    
    if existing:
        return jsonify({'error': 'This time slot is already booked'}), 400
    
    appointment.appointment_date = new_date
    appointment.appointment_time = new_time
    db.session.commit()
    
    return jsonify({'message': 'Appointment rescheduled', 'appointment': appointment.to_dict()}), 200

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@patient_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    patient = get_patient_profile()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != patient.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if appointment.status != 'booked':
        return jsonify({'error': 'Can only cancel booked appointments'}), 400
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Appointment cancelled'}), 200

@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
@patient_required
def get_my_appointments():
    """Get patient's appointments"""
    patient = get_patient_profile()
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(patient_id=patient.id)
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    
    return jsonify([apt.to_dict() for apt in appointments]), 200

@patient_bp.route('/treatments', methods=['GET'])
@jwt_required()
@patient_required
def get_treatment_history():
    """Get patient's treatment history"""
    patient = get_patient_profile()
    
    treatments = Treatment.query.filter_by(patient_id=patient.id)\
        .order_by(Treatment.created_at.desc()).all()
    
    return jsonify([t.to_dict() for t in treatments]), 200