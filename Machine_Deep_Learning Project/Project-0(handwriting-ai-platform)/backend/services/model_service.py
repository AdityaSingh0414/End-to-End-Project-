import os
import pickle
import numpy as np
import tensorflow as tf

class ModelService:
    _digit_model = None
    _letter_model = None
    _tokenizer = None
    _is_loaded = False

    @classmethod
    def load_models(cls):
        """
        Lazy loads the digit and letter models and tokenizer.
        """
        if cls._is_loaded:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, '../../models')
        
        digit_path = os.path.join(models_dir, 'cnn_digit_model.h5')
        letter_path = os.path.join(models_dir, 'crnn_letter_model.h5')
        tokenizer_path = os.path.join(models_dir, 'tokenizer.pkl')

        print("Lazy loading TensorFlow models...")
        
        # Disable GPU logging/warnings if necessary
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

        if not os.path.exists(digit_path) or not os.path.exists(letter_path) or not os.path.exists(tokenizer_path):
            raise FileNotFoundError(
                f"Model files not found. Please ensure cnn_digit_model.h5, crnn_letter_model.h5, "
                f"and tokenizer.pkl exist in {models_dir}. Run the model training script first."
            )

        # Load models
        cls._digit_model = tf.keras.models.load_model(digit_path)
        cls._letter_model = tf.keras.models.load_model(letter_path)
        
        # Load tokenizer
        with open(tokenizer_path, 'rb') as f:
            cls._tokenizer = pickle.load(f)

        cls._is_loaded = True
        print("TensorFlow models and tokenizer loaded successfully!")

    @classmethod
    def predict(cls, char_images, mode='auto'):
        """
        Predicts character labels for a list of 28x28 grayscale images.
        - char_images: list of 28x28 numpy arrays.
        - mode: 'digits', 'letters', or 'auto'.
        - Returns: list of lists of (character, confidence) sorted by confidence.
        """
        if not char_images:
            return []

        # Ensure models are loaded
        cls.load_models()

        # Reshape images to (batch_size, 28, 28, 1) and normalize to [0, 1]
        batch = np.array(char_images).reshape(-1, 28, 28, 1).astype('float32')
        if np.max(batch) > 1.0:
            batch /= 255.0

        results = []

        if mode == 'digits':
            # Run inference on digit model only
            preds = cls._digit_model.predict(batch, verbose=0)
            for pred in preds:
                char_preds = []
                for idx, conf in enumerate(pred):
                    char_preds.append((cls._tokenizer['digits'][idx], float(conf)))
                # Sort by confidence descending
                char_preds = sorted(char_preds, key=lambda x: x[1], reverse=True)
                results.append(char_preds)

        elif mode == 'letters':
            # Run inference on letter model only
            preds = cls._letter_model.predict(batch, verbose=0)
            for pred in preds:
                char_preds = []
                for idx, conf in enumerate(pred):
                    char_preds.append((cls._tokenizer['letters'][idx], float(conf)))
                char_preds = sorted(char_preds, key=lambda x: x[1], reverse=True)
                results.append(char_preds)

        else: # auto mode: runs parallel inference on both models
            digit_preds = cls._digit_model.predict(batch, verbose=0)
            letter_preds = cls._letter_model.predict(batch, verbose=0)

            for d_pred, l_pred in zip(digit_preds, letter_preds):
                d_max_idx = np.argmax(d_pred)
                d_max_conf = d_pred[d_max_idx]

                l_max_idx = np.argmax(l_pred)
                l_max_conf = l_pred[l_max_idx]

                char_preds = []
                # Compare max confidence to select digit vs letter model
                if d_max_conf > l_max_conf:
                    # Choose digit predictions
                    for idx, conf in enumerate(d_pred):
                        char_preds.append((cls._tokenizer['digits'][idx], float(conf)))
                else:
                    # Choose letter predictions
                    for idx, conf in enumerate(l_pred):
                        char_preds.append((cls._tokenizer['letters'][idx], float(conf)))

                char_preds = sorted(char_preds, key=lambda x: x[1], reverse=True)
                results.append(char_preds)

        return results
