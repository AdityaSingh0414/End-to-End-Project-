import os
import base64
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, send_file
from segmentation.opencv_segmenter import OpenCVSegmenter
from services.model_service import ModelService
from services.corrector_service import DictionaryCorrector
from utils.logger import AnalyticsLogger

api_bp = Blueprint('api', __name__)
corrector = DictionaryCorrector()

# Mock training metrics for the dashboard charts (realistic curves representing model training)
TRAINING_METRICS = {
    "digit_model": {
        "epochs": [1, 2],
        "accuracy": [0.952, 0.981],
        "val_accuracy": [0.974, 0.985],
        "loss": [0.158, 0.059],
        "val_loss": [0.082, 0.047]
    },
    "letter_model": {
        "epochs": [1, 2, 3, 4, 5],
        "accuracy": [0.724, 0.881, 0.932, 0.959, 0.974],
        "val_accuracy": [0.812, 0.903, 0.941, 0.962, 0.978],
        "loss": [0.943, 0.412, 0.228, 0.137, 0.084],
        "val_loss": [0.612, 0.324, 0.198, 0.124, 0.076]
    }
}

@api_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() or {}
        
        # Read parameters
        image_data = data.get('image')
        mode = data.get('mode', 'auto') # 'digits', 'letters', 'auto'
        autocorrect_enabled = data.get('autocorrect', True)
        dilation = int(data.get('dilation', 1))
        split_ratio = float(data.get('split_ratio', 1.4))
        filename = data.get('filename', 'canvas_draw.png')
        
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
            
        # 1. Preprocess & Segment using OpenCV
        try:
            img = OpenCVSegmenter.preprocess_image(image_data)
            segmented_items, annotated_img = OpenCVSegmenter.segment_image(
                img, stroke_dilation=dilation, split_threshold_ratio=split_ratio
            )
        except Exception as e:
            return jsonify({"error": f"Image segmentation failed: {str(e)}"}), 400
            
        if not segmented_items:
            return jsonify({
                "raw_text": "",
                "corrected_text": "",
                "avg_confidence": 0.0,
                "mode": mode,
                "characters": [],
                "annotated_image": image_data # Return original if no segments
            })

        # 2. Extract character images to run through Deep Learning models
        char_nodes = [item for item in segmented_items if not item['is_space']]
        char_images = [node['char_image'] for node in char_nodes]
        
        # 3. Model Inference (Batch)
        predictions = []
        if char_images:
            try:
                predictions = ModelService.predict(char_images, mode=mode)
            except Exception as e:
                return jsonify({"error": f"Model inference failed: {str(e)}. Make sure models are trained."}), 500

        # Map predictions back to the segmented items
        pred_idx = 0
        for item in segmented_items:
            if item['is_space']:
                item['predictions'] = [(" ", 1.0)]
            else:
                item['predictions'] = predictions[pred_idx]
                pred_idx += 1
                # Remove numpy array before serializing
                if 'char_image' in item:
                    del item['char_image']

        # 4. Dictionary Spelling Auto-Correction
        # We group characters into words by splitting at spaces
        words = []
        current_word_chars = []
        
        for item in segmented_items:
            if item['is_space']:
                if current_word_chars:
                    words.append(current_word_chars)
                    current_word_chars = []
            else:
                current_word_chars.append(item)
        if current_word_chars:
            words.append(current_word_chars)
            
        corrected_words = []
        raw_words = []
        
        for word in words:
            # Word predictions is a list of predictions for each character in the word
            word_preds = [char_node['predictions'] for char_node in word]
            
            # Raw text (top 1 characters)
            raw_w = "".join([preds[0][0] for preds in word_preds])
            raw_words.append(raw_w)
            
            # Corrected word
            if autocorrect_enabled and mode != 'digits':
                corr_w, corr_conf, corr_method = corrector.correct_word(word_preds)
                corrected_words.append(corr_w)
            else:
                corrected_words.append(raw_w)

        raw_text = " ".join(raw_words)
        corrected_text = " ".join(corrected_words)

        # Calculate average confidence
        all_confidences = []
        for node in char_nodes:
            if 'predictions' in node and node['predictions']:
                all_confidences.append(node['predictions'][0][1])
        avg_confidence = np.mean(all_confidences) if all_confidences else 0.0

        # Encode annotated image to Base64 to show bounding boxes in UI
        _, buffer = cv2.imencode('.png', annotated_img)
        annotated_base64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')

        # 5. Log prediction details in analytics logger
        character_details = []
        for node in segmented_items:
            if node['is_space']:
                character_details.append({"is_space": True})
            else:
                character_details.append({
                    "is_space": False,
                    "x": node['x'], "y": node['y'], "w": node['w'], "h": node['h'],
                    "top_predictions": [{"char": char, "conf": round(conf, 4)} for char, conf in node['predictions'][:5]]
                })

        AnalyticsLogger.log_prediction(
            filename=filename,
            mode=mode,
            raw_text=raw_text,
            corrected_text=corrected_text,
            avg_confidence=avg_confidence,
            character_details=character_details
        )

        return jsonify({
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "avg_confidence": round(float(avg_confidence), 4),
            "mode": mode,
            "characters": segmented_items,
            "annotated_image": annotated_base64
        })

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    logs = AnalyticsLogger.get_logs()
    return jsonify({
        "prediction_history": logs,
        "training_curves": TRAINING_METRICS
    })

@api_bp.route('/export-csv', methods=['GET'])
def export_csv():
    _, csv_path = AnalyticsLogger.get_paths()
    if not os.path.exists(csv_path):
        # Create an empty CSV file with header if it doesn't exist
        AnalyticsLogger.log_prediction("test", "auto", "test", "test", 1.0, [])
        
    return send_file(
        csv_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name='prediction_logs.csv'
    )

@api_bp.route('/clear-logs', methods=['POST'])
def clear_logs():
    AnalyticsLogger.clear_logs()
    return jsonify({"success": True, "message": "All logs cleared successfully"})
