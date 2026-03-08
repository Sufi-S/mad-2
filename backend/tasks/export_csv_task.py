from backend.tasks.celery_worker import celery
from backend.services.report_service import ReportService
from backend.models.patient_model import Patient
from backend.models.user_model import User
import logging
import os
from celery.result import AsyncResult
import json

logger = logging.getLogger(__name__)

@celery.task(name='tasks.export_patient_treatment_csv', bind=True)
def export_patient_treatment_csv(self, patient_id):
    """
    Export patient treatment history as CSV
    This is a user-triggered async task
    """
    logger.info(f"Starting CSV export for patient {patient_id}")
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Generating CSV...'}
        )
        
        # Generate CSV
        csv_data, error = ReportService.generate_patient_treatment_csv(patient_id)
        
        if error:
            self.update_state(
                state='FAILURE',
                meta={'error': error}
            )
            return {'error': error}
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 70, 'total': 100, 'status': 'Saving file...'}
        )
        
        # Save CSV to file (optional)
        patient = Patient.query.get(patient_id)
        filename = f"treatment_history_{patient.name}_{patient_id}.csv"
        filepath = os.path.join('/tmp', filename)
        
        with open(filepath, 'w') as f:
            f.write(csv_data)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'status': 'Preparing download...'}
        )
        
        # Store result
        result = {
            'status': 'SUCCESS',
            'filename': filename,
            'filepath': filepath,
            'patient_id': patient_id,
            'patient_name': patient.name,
            'download_url': f'/api/patient/download-csv/{patient_id}'
        }
        
        # Cache result in Redis for retrieval
        from backend.extensions import redis_client
        redis_client.setex(
            f"export:{self.request.id}",
            3600,  # 1 hour expiry
            json.dumps(result)
        )
        
        logger.info(f"CSV export completed for patient {patient_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in CSV export: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@celery.task(name='tasks.check_export_status')
def check_export_status(task_id):
    """
    Check status of export task
    """
    result = AsyncResult(task_id, app=celery)
    
    if result.ready():
        if result.successful():
            return {
                'status': 'SUCCESS',
                'result': result.result
            }
        else:
            return {
                'status': 'FAILED',
                'error': str(result.result)
            }
    else:
        return {
            'status': 'PROCESSING',
            'progress': result.info
        }

@celery.task(name='tasks.cleanup_old_exports')
def cleanup_old_exports():
    """
    Clean up old export files (runs daily)
    """
    try:
        import os
        import time
        
        # Remove files older than 24 hours
        cutoff = time.time() - (24 * 3600)
        
        for filename in os.listdir('/tmp'):
            if filename.startswith('treatment_history_') and filename.endswith('.csv'):
                filepath = os.path.join('/tmp', filename)
                if os.path.getctime(filepath) < cutoff:
                    os.remove(filepath)
                    logger.info(f"Removed old export: {filename}")
                    
    except Exception as e:
        logger.error(f"Error cleaning up exports: {str(e)}")