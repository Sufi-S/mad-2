from backend.models.appointment_model import Appointment
from backend.models.treatment_model import Treatment
from backend.models.doctor_model import Doctor
from backend.models.patient_model import Patient
from datetime import datetime, timedelta
import csv
from io import StringIO

class ReportService:
    @staticmethod
    def generate_monthly_doctor_report(doctor_id, year, month):
        """Generate monthly report for a doctor"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None, 'Doctor not found'
        
        # Get all appointments for the month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date.between(start_date, end_date),
            Appointment.status == 'completed'
        ).all()
        
        # Get treatments for these appointments
        treatment_data = []
        for apt in appointments:
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
            if treatment:
                treatment_data.append({
                    'appointment_id': apt.id,
                    'patient_name': apt.patient.name if apt.patient else 'Unknown',
                    'date': apt.appointment_date.isoformat(),
                    'diagnosis': treatment.diagnosis,
                    'prescription': treatment.prescription,
                    'next_visit': treatment.next_visit_date.isoformat() if treatment.next_visit_date else 'Not scheduled'
                })
        
        # Generate HTML report
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Monthly Activity Report - Dr. {doctor.name}</h1>
            <h2>{month}/{year}</h2>
            
            <div class="summary">
                <p><strong>Total Appointments:</strong> {len(appointments)}</p>
                <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <table>
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Diagnosis</th>
                    <th>Prescription</th>
                    <th>Next Visit</th>
                </tr>
        """
        
        for t in treatment_data:
            html += f"""
                <tr>
                    <td>{t['date']}</td>
                    <td>{t['patient_name']}</td>
                    <td>{t['diagnosis']}</td>
                    <td>{t['prescription']}</td>
                    <td>{t['next_visit']}</td>
                </tr>
            """
        
        html += """
            </table>
            <p><em>This is an automated report from the Hospital Management System</em></p>
        </body>
        </html>
        """
        
        return html, None
    
    @staticmethod
    def generate_patient_treatment_csv(patient_id):
        """Generate CSV of patient's treatment history"""
        patient = Patient.query.get(patient_id)
        if not patient:
            return None, 'Patient not found'
        
        treatments = Treatment.query.filter_by(patient_id=patient_id)\
            .order_by(Treatment.created_at.desc()).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Treatment ID', 'Date', 'Doctor', 'Diagnosis', 
            'Prescription', 'Notes', 'Next Visit Date'
        ])
        
        # Write data
        for t in treatments:
            writer.writerow([
                t.id,
                t.created_at.strftime('%Y-%m-%d') if t.created_at else 'N/A',
                t.doctor.name if t.doctor else 'N/A',
                t.diagnosis,
                t.prescription,
                t.notes,
                t.next_visit_date.isoformat() if t.next_visit_date else 'N/A'
            ])
        
        return output.getvalue(), None