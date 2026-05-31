# AURA: Handwritten Character & Word Recognition Platform

AURA is an end-to-end, high-performance handwriting segmentation and recognition platform. The system features a custom deep learning engine (TensorFlow Keras), an OpenCV computer vision preprocessing and splitting pipeline, and a spelling auto-correction search engine to deliver real-time digit and letter sequence recognition.

---

## Key Technical Features

### 1. Dual-Model Deep Learning Inference (TensorFlow)
- **CNN Digit Classifier (MNIST)**: A custom Convolutional Neural Network processing grayscale canvas slices (28x28x1). Achieves **~98.7%** validation accuracy for numerical inputs (0-9).
- **CRNN Letter Classifier (EMNIST)**: A Convolutional Recurrent Neural Network (Conv2D -> Reshape -> Bidirectional LSTM -> Dense) designed to capture horizontal letter strokes. Classifies 26 alphabet characters (A-Z).
- **Intelligent Auto-Mode**: Operates parallel inference on both models for each character and selects predictions dynamically using comparative relative confidence scores.

### 2. OpenCV Segmentation & Splitting Pipeline
- **Binarization & Background Inversion**: Evaluates canvas border gradients to adaptively apply Otsu thresholding, handling light/dark modes.
- **Stroke Dilation**: Applies morphological kernel dilations to bridge broken pen strokes (like crossbars in "A" or "H") into unified character envelopes.
- **Valley-Splitting algorithm**: Analyzes column-wise pixel projection profiles to identify local minima (low-ink valleys) and splits overlapping or cursive characters.
- **Space Detection**: Computes space-gap medians dynamically. Gap sizes exceeding `1.7 * median_gap` insert a space character (`" "`) to segment words.

### 3. Spelling Auto-Correction Search Engine
- **Beam-Search Joint Probability Search**: Given the top-5 predicted characters for each letter, compiles candidates and evaluates the joint probability product:
  $$P(W) = \prod_{i=1}^{L} P(c_i)$$
  Matches strings against an embedded vocabulary dictionary of the 1000+ most common English words.
- **Levenshtein Distance Fallback**: Calculates dynamic-programming edit distance to fall back to the closest dictionary word when joint probability falls below threshold.

---

## Directory Architecture

```
handwriting-ai-platform/
├── models/                  # Saved .h5 neural nets & character maps
│   ├── cnn_digit_model.h5
│   ├── crnn_letter_model.h5
│   └── tokenizer.pkl
├── training/                # Training pipelines
│   ├── build_models.py      # Automates dataset setup & training
│   ├── digit_training.ipynb
│   └── letter_training.ipynb
├── backend/                 # Flask API Services
│   ├── app.py               # Application entry point
│   ├── routes/              # HTTP endpoint controllers
│   ├── services/            # Inference & Correction modules
│   └── segmentation/        # OpenCV image split functions
├── frontend/                # React (Vite) dashboard UI
│   ├── src/                 # Workspace components, charts, and API client
│   └── package.json
├── tests/                   # Verification test suite
│   └── test_pipeline.py
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js v18+

### 1. Build and Train Deep Learning Models
First, run the build script to train models and output assets:
```bash
# From project root directory
py -3.10 training/build_models.py
```
This script downloads MNIST, generates a synthetic letter dataset (using augmented system font characters), compiles both models, trains them, and saves the binary artifacts to the `/models` directory.

### 2. Launch Backend Flask Server
Install dependencies and run the API:
```bash
# Navigate to backend and install requirements
cd backend
py -3.10 -m pip install -r requirements.txt

# Start backend server (runs on port 5000)
py -3.10 app.py
```

### 3. Launch React Frontend
```bash
# Navigate to frontend and start developer server
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Verification Tests
Verify component integration using the automated verification suite:
```bash
# From project root
py -3.10 tests/test_pipeline.py
```
This tests:
- Image loading, Otsu thresholding, and segmentation coordinate mapping.
- Model loader configurations and dummy character inference shapes.
- Joint-probability spelling correction search and Levenshtein edit distance logic.
