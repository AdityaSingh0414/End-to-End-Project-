import os
import json
import csv
from datetime import datetime

class AnalyticsLogger:
    @staticmethod
    def get_paths():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        analytics_dir = os.path.join(base_dir, '../../analytics')
        logs_dir = os.path.join(analytics_dir, 'logs')
        csv_dir = os.path.join(analytics_dir, 'csv_exports')
        
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(csv_dir, exist_ok=True)
        
        json_log_path = os.path.join(logs_dir, 'predictions.json')
        csv_log_path = os.path.join(csv_dir, 'predictions.csv')
        
        return json_log_path, csv_log_path

    @staticmethod
    def log_prediction(filename, mode, raw_text, corrected_text, avg_confidence, character_details):
        """
        Logs a single prediction transaction.
        - filename: name of processed image or 'canvas_draw'
        - mode: classification mode ('digits', 'letters', 'auto')
        - raw_text: raw uncorrected model prediction string
        - corrected_text: dictionary-corrected final prediction
        - avg_confidence: mean confidence of top character predictions
        - character_details: list of character predictions and confidences for deep analytics
        """
        json_path, csv_path = AnalyticsLogger.get_paths()
        
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "filename": filename,
            "mode": mode,
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "avg_confidence": round(float(avg_confidence), 4),
            "characters": character_details
        }
        
        # 1. Update JSON logs
        logs = []
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
                
        logs.append(log_entry)
        
        # Keep logs at reasonable count (e.g. 1000 items)
        if len(logs) > 1000:
            logs = logs[-1000:]
            
        try:
            with open(json_path, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Failed to write json log: {e}")
            
        # 2. Update CSV logs
        file_exists = os.path.exists(csv_path)
        try:
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    # Write headers
                    writer.writerow(["Timestamp", "Filename", "Mode", "Raw Text", "Corrected Text", "Average Confidence"])
                writer.writerow([
                    timestamp, 
                    filename, 
                    mode, 
                    raw_text, 
                    corrected_text, 
                    round(float(avg_confidence), 4)
                ])
        except Exception as e:
            print(f"Failed to append to csv log: {e}")

    @staticmethod
    def get_logs():
        """
        Reads prediction history from JSON.
        """
        json_path, _ = AnalyticsLogger.get_paths()
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    @staticmethod
    def clear_logs():
        """
        Clears all prediction logs.
        """
        json_path, csv_path = AnalyticsLogger.get_paths()
        if os.path.exists(json_path):
            os.remove(json_path)
        if os.path.exists(csv_path):
            os.remove(csv_path)
