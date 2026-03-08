from backend.extensions import db
from backend.models.user_model import User
from backend.models.department_model import Department
from backend.config import Config


def init_database():
    """Create tables and add initial data"""

    # Create tables
    db.create_all()

    # -------- Create Admin --------

    admin = User.query.filter_by(
        username=Config.ADMIN_USERNAME
    ).first()

    if not admin:

        admin = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            role='admin'
        )

        admin.set_password(Config.ADMIN_PASSWORD)

        db.session.add(admin)

        print("Admin user created")

    else:

        print("Admin already exists")

    # -------- Create Departments --------

    departments = [

        ('Cardiology', 'Heart and cardiovascular system'),

        ('Dermatology', 'Skin, hair, and nails'),

        ('Neurology', 'Brain and nervous system'),

        ('Pediatrics', 'Medical care for children'),

        ('Orthopedics', 'Bones and joints'),

        ('Ophthalmology', 'Eye care'),

        ('Dentistry', 'Dental care'),

        ('Psychiatry', 'Mental health'),

    ]

    for name, desc in departments:

        existing = Department.query.filter_by(
            name=name
        ).first()

        if not existing:

            dept = Department(
                name=name,
                description=desc
            )

            db.session.add(dept)

    db.session.commit()

    print("Database initialized successfully")