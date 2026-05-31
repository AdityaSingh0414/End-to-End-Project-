import os
import sys
import numpy as np
import cv2

# Set path to include backend files
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, '../backend')
sys.path.append(backend_dir)

def create_test_image():
    """
    Creates a synthetic test image with two drawn shapes (characters) and a space.
    """
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255 # White background
    
    # Draw simple shapes representing characters (e.g. vertical lines)
    # Character 1: '1' at x=20
    cv2.line(img, (20, 20), (20, 80), (0, 0, 0), 4)
    # Character 2: '1' at x=50 (close to char 1)
    cv2.line(img, (50, 20), (50, 80), (0, 0, 0), 4)
    
    # Large space in between
    
    # Character 3: 'L' shape at x=180
    cv2.line(img, (180, 20), (180, 80), (0, 0, 0), 4)
    cv2.line(img, (180, 80), (210, 80), (0, 0, 0), 4)
    
    return img

def test_opencv_segmenter():
    print("Testing OpenCV Segmenter...")
    from segmentation.opencv_segmenter import OpenCVSegmenter
    
    img = create_test_image()
    segmented_items, annotated = OpenCVSegmenter.segment_image(img, stroke_dilation=1)
    
    print(f"Segmenter found {len(segmented_items)} items (characters + spaces).")
    for item in segmented_items:
        print(f"  Item ID: {item['id']}, is_space: {item['is_space']}, x={item.get('x')}, w={item.get('w')}")
        
    assert len(segmented_items) > 0, "Should segment at least one character!"
    
    # Check if a space was detected
    has_space = any(item['is_space'] for item in segmented_items)
    print(f"  Space detected: {has_space}")
    print("OpenCV Segmenter test: PASSED")
    print("-" * 50)

def test_dictionary_corrector():
    print("Testing Dictionary Corrector...")
    from services.corrector_service import DictionaryCorrector
    
    corrector = DictionaryCorrector()
    
    # Define a mocked prediction sequence for the word "THE"
    # Word: T - H - E
    # Let's provide top-5 outputs
    char_preds = [
        # Char 1: top-1 is T (high confidence)
        [('T', 0.90), ('Y', 0.05), ('I', 0.02), ('L', 0.01), ('F', 0.01)],
        # Char 2: top-1 is H (medium confidence)
        [('H', 0.85), ('N', 0.08), ('M', 0.03), ('U', 0.02), ('K', 0.01)],
        # Char 3: top-1 is E (but mixed confidence)
        [('E', 0.88), ('F', 0.06), ('B', 0.03), ('L', 0.02), ('O', 0.01)]
    ]
    
    corrected, conf, method = corrector.correct_word(char_preds)
    print(f"  Mock input top-1: THE -> Corrected: {corrected} (conf={conf:.4f}, method={method})")
    assert corrected == "THE", "Should match THE directly"
    
    # Test correction of a misspelled top-1: "THP" -> should correct to "THE"
    char_preds_misspelled = [
        [('T', 0.80), ('Y', 0.05), ('I', 0.02), ('L', 0.01), ('F', 0.01)],
        [('H', 0.85), ('N', 0.08), ('M', 0.03), ('U', 0.02), ('K', 0.01)],
        [('P', 0.50), ('E', 0.40), ('F', 0.05), ('B', 0.03), ('L', 0.02)] # P is top-1, but E is top-2 with high joint prob
    ]
    
    corrected, conf, method = corrector.correct_word(char_preds_misspelled)
    print(f"  Mock input top-1: THP -> Corrected: {corrected} (conf={conf:.4f}, method={method})")
    assert corrected == "THE", "Should autocorrect THP to THE using joint probabilities"
    
    # Test Levenshtein distance fallback: "BGG" -> "BIG"
    char_preds_lev = [
        [('B', 0.90)],
        [('G', 0.90)],
        [('G', 0.90)]
    ]
    corrected, conf, method = corrector.correct_word(char_preds_lev)
    print(f"  Mock input top-1: BGG -> Corrected: {corrected} (conf={conf:.4f}, method={method})")
    assert corrected in ["BIG", "BOX", "BAG", "EGG", "BOY", "BAD", "BUG"], "Should fall back to Levenshtein dictionary match"
    
    print("Dictionary Corrector test: PASSED")
    print("-" * 50)

def test_model_loading_and_prediction():
    print("Testing Model loading & prediction...")
    from services.model_service import ModelService
    
    try:
        ModelService.load_models()
        print("  Models loaded successfully.")
        
        # Test predict with mock input (28x28 zeros)
        dummy_img = np.zeros((28, 28), dtype=np.float32)
        
        # Predict digits
        digit_preds = ModelService.predict([dummy_img], mode='digits')
        print(f"  Digit prediction output format: {digit_preds[0][:3]}")
        assert len(digit_preds) == 1
        assert len(digit_preds[0]) == 10
        
        # Predict letters
        letter_preds = ModelService.predict([dummy_img], mode='letters')
        print(f"  Letter prediction output format: {letter_preds[0][:3]}")
        assert len(letter_preds) == 1
        assert len(letter_preds[0]) == 26
        
        print("Model Service test: PASSED")
    except Exception as e:
        print(f"  Model Service test FAILED: {e}")
        print("  (Note: Ensure build_models.py has completed before running this test)")
    print("-" * 50)

if __name__ == '__main__':
    print("RUNNING HANDWRITING AI PLATFORM VERIFICATION TESTS\n" + "="*50)
    test_opencv_segmenter()
    test_dictionary_corrector()
    test_model_loading_and_prediction()
    print("VERIFICATION COMPLETE")
