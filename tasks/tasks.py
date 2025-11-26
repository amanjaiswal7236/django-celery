import os
import time
import logging
from celery import shared_task
from django.utils import timezone
from .models import Task, TaskLog
from .utils import send_task_update

logger = logging.getLogger('tasks')


def log_task_message(task_obj, message, level='INFO'):
    """Helper to log messages for a task"""
    TaskLog.objects.create(
        task=task_obj,
        message=message,
        level=level
    )
    logger.log(
        getattr(logging, level, logging.INFO),
        f"Task {task_obj.id}: {message}"
    )


@shared_task(bind=True, max_retries=3)
def process_file_task(self, task_id):
    """Process a file (example: image resizing, PDF conversion, etc.)"""
    task = Task.objects.get(id=task_id)
    task.mark_as_running()
    task.celery_task_id = self.request.id
    task.save()
    
    log_task_message(task, "Starting file processing task")
    send_task_update(task)
    
    try:
        # Simulate file processing with progress updates
        file_path = task.parameters.get('file_path', '')
        operation = task.parameters.get('operation', 'resize')
        
        if not file_path:
            raise ValueError("File path not provided")
        
        log_task_message(task, f"Processing file: {file_path}")
        
        # Simulate processing steps
        steps = ['Reading file', 'Validating format', 'Processing', 'Saving result']
        for i, step in enumerate(steps):
            time.sleep(2)  # Simulate work
            progress = int((i + 1) / len(steps) * 100)
            task.update_progress(progress)
            log_task_message(task, f"Step {i+1}/{len(steps)}: {step}")
            send_task_update(task)
        
        result = f"File processed successfully: {file_path}"
        task.mark_as_success(result)
        log_task_message(task, "File processing completed successfully")
        send_task_update(task)
        
        return result
        
    except Exception as exc:
        error_msg = str(exc)
        task.mark_as_failed(error_msg)
        log_task_message(task, f"File processing failed: {error_msg}", level='ERROR')
        send_task_update(task)
        raise


@shared_task(bind=True, max_retries=3)
def scraping_task(self, task_id):
    """Web scraping task"""
    task = Task.objects.get(id=task_id)
    task.mark_as_running()
    task.celery_task_id = self.request.id
    task.save()
    
    log_task_message(task, "Starting web scraping task")
    send_task_update(task)
    
    try:
        url = task.parameters.get('url', '')
        selectors = task.parameters.get('selectors', {})
        
        if not url:
            raise ValueError("URL not provided")
        
        log_task_message(task, f"Scraping URL: {url}")
        
        # Simulate scraping with progress
        import requests
        from bs4 import BeautifulSoup
        
        task.update_progress(10)
        send_task_update(task)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        task.update_progress(40)
        log_task_message(task, "Page fetched successfully")
        send_task_update(task)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        task.update_progress(60)
        send_task_update(task)
        
        scraped_data = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            scraped_data[key] = [elem.get_text(strip=True) for elem in elements[:10]]
            log_task_message(task, f"Extracted {len(scraped_data[key])} items for '{key}'")
        
        task.update_progress(90)
        send_task_update(task)
        
        result = f"Scraped {len(scraped_data)} fields from {url}"
        task.mark_as_success(str(scraped_data))
        log_task_message(task, "Scraping completed successfully")
        send_task_update(task)
        
        return result
        
    except Exception as exc:
        error_msg = str(exc)
        task.mark_as_failed(error_msg)
        log_task_message(task, f"Scraping failed: {error_msg}", level='ERROR')
        send_task_update(task)
        raise


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, task_id):
    """Generate a report (example: Excel, PDF, etc.)"""
    task = Task.objects.get(id=task_id)
    task.mark_as_running()
    task.celery_task_id = self.request.id
    task.save()
    
    log_task_message(task, "Starting report generation task")
    send_task_update(task)
    
    try:
        report_type = task.parameters.get('report_type', 'excel')
        data_source = task.parameters.get('data_source', [])
        
        log_task_message(task, f"Generating {report_type} report")
        
        # Simulate report generation
        steps = ['Collecting data', 'Processing data', 'Formatting report', 'Generating file']
        for i, step in enumerate(steps):
            time.sleep(2)
            progress = int((i + 1) / len(steps) * 100)
            task.update_progress(progress)
            log_task_message(task, f"Step {i+1}/{len(steps)}: {step}")
            send_task_update(task)
        
        # Simulate creating a report file
        if report_type == 'excel':
            import pandas as pd
            df = pd.DataFrame(data_source if data_source else {'Sample': ['Data']})
            report_path = f"media/reports/report_{task.id}.xlsx"
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            df.to_excel(report_path, index=False)
            result = f"Report generated: {report_path}"
        else:
            result = f"Report generated successfully (type: {report_type})"
        
        task.mark_as_success(result)
        log_task_message(task, "Report generation completed successfully")
        send_task_update(task)
        
        return result
        
    except Exception as exc:
        error_msg = str(exc)
        task.mark_as_failed(error_msg)
        log_task_message(task, f"Report generation failed: {error_msg}", level='ERROR')
        send_task_update(task)
        raise

