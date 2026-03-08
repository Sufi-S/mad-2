from backend.extensions import db, bcrypt
from backend.models.user_model import User
from backend.models.patient_model import Patient
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user and return tokens"""
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return {'error': 'Account is deactivated'}, None
            
            # FIXED: Convert user.id to string for JWT identity
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={'role': user.role},
                expires_delta=timedelta(hours=1)
            )
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }, None
        
        return None, {'error': 'Invalid credentials'}
    
    @staticmethod
    def register_patient(data):
        """Register a new patient"""
        # Check existing user
        if User.query.filter_by(username=data.get('username')).first():
            return None, {'error': 'Username already exists'}
        
        if User.query.filter_by(email=data.get('email')).first():
            return None, {'error': 'Email already exists'}
        
        # Create user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role='patient'
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            name=data.get('name'),
            phone=data.get('phone'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            emergency_contact=data.get('emergency_contact')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return {'user': user.to_dict(), 'profile': patient.to_dict()}, None