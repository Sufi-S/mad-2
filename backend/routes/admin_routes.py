from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models.user_model import User
from backend.models.doctor_model import Doctor
from backend.models.patient_model import Patient
from backend.models.appointment_model import Appointment
from backend.models.department_model import Department
from functools import wraps
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def dashboard():
    """Admin dashboard stats"""
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    
    # Appointment stats
    booked = Appointment.query.filter_by(status='booked').count()
    completed = Appointment.query.filter_by(status='completed').count()
    cancelled = Appointment.query.filter_by(status='cancelled').count()
    
    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'appointment_stats': {
            'booked': booked,
            'completed': completed,
            'cancelled': cancelled
        }
    }), 200

@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
@admin_required
def get_doctors():
    """Get all doctors"""
    doctors = Doctor.query.all()
    return jsonify([doctor.to_dict() for doctor in doctors]), 200

@admin_bp.route('/doctors', methods=['POST'])
@jwt_required()
@admin_required
def add_doctor():
    """Add new doctor"""
    data = request.get_json()
    
    # Check if user exists
    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user account for doctor
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        role='doctor'
    )
    user.set_password(data.get('password', 'doctor123'))  # Default password
    
    db.session.add(user)
    db.session.flush()
    
    # Create doctor profile
    import json
    doctor = Doctor(
        user_id=user.id,
        name=data.get('name'),
        specialization=data.get('specialization'),
        qualification=data.get('qualification'),
        experience_years=data.get('experience_years'),
        consultation_fee=data.get('consultation_fee'),
        availability=json.dumps(data.get('availability', {}))
    )
    
    db.session.add(doctor)
    db.session.commit()
    
    return jsonify({'message': 'Doctor added successfully', 'doctor': doctor.to_dict()}), 201

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_doctor(doctor_id):
    """Update doctor details"""
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    
    doctor.name = data.get('name', doctor.name)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.qualification = data.get('qualification', doctor.qualification)
    doctor.experience_years = data.get('experience_years', doctor.experience_years)
    doctor.consultation_fee = data.get('consultation_fee', doctor.consultation_fee)
    
    if data.get('availability'):
        import json
        doctor.availability = json.dumps(data.get('availability'))
    
    db.session.commit()
    
    return jsonify({'message': 'Doctor updated successfully', 'doctor': doctor.to_dict()}), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_doctor(doctor_id):
    """Delete/blacklist doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Soft delete - deactivate user
    user = User.query.get(doctor.user_id)
    if user:
        user.is_active = False
    
    db.session.commit()
    
    return jsonify({'message': 'Doctor deactivated successfully'}), 200

@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
@admin_required
def get_patients():
    """Get all patients"""
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients]), 200

@admin_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_patient(patient_id):
    """Delete/blacklist patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Soft delete - deactivate user
    user = User.query.get(patient.user_id)
    if user:
        user.is_active = False
    
    db.session.commit()
    
    return jsonify({'message': 'Patient deactivated successfully'}), 200

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_appointments():
    """Get all appointments"""
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

@admin_bp.route('/search', methods=['GET'])
@jwt_required()
@admin_required
def search():
    """Search patients or doctors"""
    query = request.args.get('q', '')
    type = request.args.get('type', 'all')  # patients, doctors, all
    
    results = {}
    
    if type in ['patients', 'all']:
        patients = Patient.query.filter(
            or_(
                Patient.name.ilike(f'%{query}%'),
                Patient.phone.ilike(f'%{query}%')
            )
        ).all()
        results['patients'] = [p.to_dict() for p in patients]
    
    if type in ['doctors', 'all']:
        doctors = Doctor.query.filter(
            or_(
                Doctor.name.ilike(f'%{query}%'),
                Doctor.specialization.ilike(f'%{query}%')
            )
        ).all()
        results['doctors'] = [d.to_dict() for d in doctors]
    
    return jsonify(results), 200

@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
@admin_required
def get_departments():
    """Get all departments"""
    departments = Department.query.all()
    return jsonify([dept.to_dict() for dept in departments]), 200