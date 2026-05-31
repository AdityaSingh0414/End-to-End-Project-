import os
import pickle
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image, ImageDraw, ImageFont
import cv2

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)
random.seed(42)

# Ensure models directory exists
base_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(base_dir, '../models')
os.makedirs(models_dir, exist_ok=True)

print("Starting deep learning model build script...")

# ----------------- DIGIT MODEL (CNN) -----------------
print("\n--- 1. Training Digit Model (CNN) ---")
print("Loading MNIST digits dataset...")
mnist = tf.keras.datasets.mnist
(x_digit_train, y_digit_train), (x_digit_test, y_digit_test) = mnist.load_data()

x_digit_train = x_digit_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
x_digit_test = x_digit_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0

print(f"MNIST train shape: {x_digit_train.shape}, test shape: {x_digit_test.shape}")

def build_digit_cnn():
    model = models.Sequential([
        layers.Input(shape=(28, 28, 1)),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

digit_model = build_digit_cnn()
digit_model.summary()

print("Training CNN digit model for 2 epochs...")
digit_model.fit(
    x_digit_train, y_digit_train, 
    epochs=2, 
    batch_size=128, 
    validation_data=(x_digit_test, y_digit_test)
)

digit_model_path = os.path.join(models_dir, 'cnn_digit_model.h5')
digit_model.save(digit_model_path)
print(f"Digit model saved to {digit_model_path}")


# ----------------- LETTER MODEL (CRNN) -----------------
print("\n--- 2. Generating Synthetic Letter Dataset & Training Letter Model (CRNN) ---")

def generate_synthetic_letters():
    classes = [chr(i) for i in range(ord('A'), ord('Z') + 1)] # 26 classes (A-Z)
    images = []
    labels = []
    
    # Standard system fonts on Windows
    font_paths = [
        "arial.ttf", "times.ttf", "calibri.ttf", "cour.ttf", "georgia.ttf", "verdana.ttf", "comic.ttf"
    ]
    
    loaded_fonts = []
    for f_path in font_paths:
        try:
            loaded_fonts.append(ImageFont.truetype(f_path, 20))
        except Exception:
            pass
            
    if not loaded_fonts:
        print("System fonts not found, falling back to PIL default font.")
        loaded_fonts.append(ImageFont.load_default())
    else:
        print(f"Loaded {len(loaded_fonts)} system fonts for synthetic character generation.")
        
    # Generate variations
    for label_idx, char in enumerate(classes):
        for _ in range(200): # 200 variations per class -> 5200 total images
            img = Image.new('L', (28, 28), color=0)
            draw = ImageDraw.Draw(img)
            font = random.choice(loaded_fonts)
            
            # Center the character
            try:
                bbox = draw.textbbox((0, 0), char, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception:
                # Compatibility for older PIL versions
                w, h = draw.textsize(char, font=font) if hasattr(draw, 'textsize') else (14, 18)
                
            x = (28 - w) // 2 + random.randint(-2, 2)
            y = (28 - h) // 2 + random.randint(-2, 2)
            
            draw.text((x, y), char, fill=255, font=font)
            np_img = np.array(img)
            
            # Random cv2 augmentation: Rotation & Scaling
            angle = random.uniform(-15, 15)
            scale = random.uniform(0.85, 1.15)
            M = cv2.getRotationMatrix2D((14, 14), angle, scale)
            np_img = cv2.warpAffine(np_img, M, (28, 28), flags=cv2.INTER_LINEAR)
            
            # Morphological operations (dilation/erosion)
            if random.random() < 0.3:
                kernel = np.ones((2, 2), np.uint8)
                if random.random() < 0.5:
                    np_img = cv2.dilate(np_img, kernel, iterations=1)
                else:
                    np_img = cv2.erode(np_img, kernel, iterations=1)
                    
            # Add Gaussian noise
            if random.random() < 0.2:
                noise = np.random.normal(0, 10, np_img.shape).astype(np.float32)
                np_img = np.clip(np_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
                
            images.append(np_img)
            labels.append(label_idx)
            
    images = np.array(images).reshape(-1, 28, 28, 1).astype('float32') / 255.0
    labels = np.array(labels)
    return images, labels

print("Generating synthetic EMNIST letters...")
x_letter, y_letter = generate_synthetic_letters()
print(f"Generated synthetic letters: shape {x_letter.shape}, labels {y_letter.shape}")

# Shuffle and split
indices = np.arange(x_letter.shape[0])
np.random.shuffle(indices)
x_letter = x_letter[indices]
y_letter = y_letter[indices]

split_idx = int(0.9 * len(x_letter))
x_letter_train, x_letter_test = x_letter[:split_idx], x_letter[split_idx:]
y_letter_train, y_letter_test = y_letter[:split_idx], y_letter[split_idx:]

def build_letter_crnn():
    model = models.Sequential([
        layers.Input(shape=(28, 28, 1)),
        # Conv layer 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)), # 14x14
        # Conv layer 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)), # 7x7
        # Reshape to treat spatial height as sequence length
        layers.Reshape((7, 448)),
        # Recurrent layer
        layers.Bidirectional(layers.LSTM(64, return_sequences=False)),
        # Classification layers
        layers.Dense(64, activation='relu'),
        layers.Dense(26, activation='softmax') # 26 alphabet letters
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

letter_model = build_letter_crnn()
letter_model.summary()

print("Training CRNN letter model for 5 epochs...")
letter_model.fit(
    x_letter_train, y_letter_train,
    epochs=5,
    batch_size=64,
    validation_data=(x_letter_test, y_letter_test)
)

letter_model_path = os.path.join(models_dir, 'crnn_letter_model.h5')
letter_model.save(letter_model_path)
print(f"Letter model saved to {letter_model_path}")


# ----------------- TOKENIZER -----------------
print("\n--- 3. Saving Character Mappings (Tokenizer) ---")
tokenizer = {
    'digits': [str(i) for i in range(10)],
    'letters': [chr(i) for i in range(ord('A'), ord('Z') + 1)]
}

tokenizer_path = os.path.join(models_dir, 'tokenizer.pkl')
with open(tokenizer_path, 'wb') as f:
    pickle.dump(tokenizer, f)

print(f"Tokenizer saved to {tokenizer_path}")
print("\nAll deep learning models built and saved successfully!")
