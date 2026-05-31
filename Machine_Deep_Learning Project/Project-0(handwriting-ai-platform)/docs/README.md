# Technical Documentation & Pipeline Overview

This folder houses the detailed architecture specification papers, segmentation projection profile math summaries, and spell correction beam-search logs.

## Pipeline Architecture Details

1. **Digital Signal Preprocessing & Binarization**:
   - `cv2.threshold` with Otsu's adaptive thresholding extracts character strokes from raw image matrix arrays.
   
2. **Morphological Dilations (Stroke Merging)**:
   - Evaluates a rectangular structuring kernel size `(2,2)` over binarized pixels to connect disconnected cursive characters and dot diacritics.

3. **Valley-Splitting Vertical Projections**:
   - Aggregates vertical pixel columns. Looks for local minima in regions where bounding boxes width exceeds aspect ratios.

4. **Deep CRNN (CNN + Bidirectional LSTM)**:
   - Passes spatial features into sequence vectors. Evaluates horizontal letters sequences context to classify characters labels.

5. **Spelling Combinatorial Correction**:
   - Runs beam-search joint probability matching:
     $$P(W) = \prod P(c_i)$$
   - Leverages Levenshtein distance calculations as a spelling repair fallback.
