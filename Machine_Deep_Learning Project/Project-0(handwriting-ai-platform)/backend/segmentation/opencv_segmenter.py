import cv2
import numpy as np

class OpenCVSegmenter:
    @staticmethod
    def preprocess_image(image_input):
        """
        Loads an image from file path, base64 string, or numpy array.
        Returns BGR OpenCV image.
        """
        if isinstance(image_input, str):
            # Check if it is base64 string
            if image_input.startswith("data:image"):
                import base64
                header, encoded = image_input.split(",", 1)
                data = base64.b64decode(encoded)
                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            raise ValueError("Unsupported image input type")
            
        if img is None:
            raise ValueError("Could not decode image")
            
        return img

    @staticmethod
    def segment_image(img, stroke_dilation=1, split_threshold_ratio=1.4):
        """
        Segments the input image into individual characters and spaces.
        - Grayscale conversion
        - Otsu thresholding (auto-inverting if light background)
        - Dilation for stroke connection
        - Contour bounding boxes
        - Valley splitting for touching characters
        - Space detection using median gap heuristic
        - Outputs list of character info (with 28x28 numpy inputs) and the annotated image.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # Binarize with Otsu's thresholding.
        # Check background color by taking the mean of border pixels
        h_img, w_img = gray.shape
        border_pixels = np.concatenate([
            gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]
        ])
        border_mean = np.mean(border_pixels)
        
        # If border is light (white canvas), we need binary inversion so strokes are white.
        if border_mean > 127:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Dilation to merge fragmented strokes (e.g. crossbars in A/H, dots in i/j)
        if stroke_dilation > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            dilated = cv2.dilate(thresh, kernel, iterations=stroke_dilation)
        else:
            dilated = thresh.copy()

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        initial_boxes = []
        for ctr in contours:
            x, y, w, h = cv2.boundingRect(ctr)
            # Remove tiny noise boxes
            if w > 2 and h > 2:
                initial_boxes.append((x, y, w, h))
                
        # Sort left-to-right
        initial_boxes = sorted(initial_boxes, key=lambda b: b[0])
        
        # Valley splitting for merged/cursive chars
        final_boxes = []
        for box in initial_boxes:
            x, y, w, h = box
            # If the box is extremely wide compared to its height, split it using vertical profile
            if w > split_threshold_ratio * h and w > 16:
                roi = thresh[y:y+h, x:x+w]
                # Column-wise sum of white pixels
                proj = np.sum(roi, axis=0)
                
                # Smooth the vertical projection profile
                kernel_size = min(5, w // 3)
                if kernel_size > 1:
                    proj_smoothed = np.convolve(proj, np.ones(kernel_size)/kernel_size, mode='same')
                else:
                    proj_smoothed = proj
                
                # Search for local minima in the inner 50% of the box
                minima = []
                edge_margin = int(w * 0.25)
                for idx in range(edge_margin, w - edge_margin):
                    if proj_smoothed[idx] < proj_smoothed[idx - 1] and proj_smoothed[idx] < proj_smoothed[idx + 1]:
                        minima.append((idx, proj_smoothed[idx]))
                
                if minima:
                    # Pick the minimum projection (deepest valley - least ink)
                    minima = sorted(minima, key=lambda m: m[1])
                    split_col = minima[0][0]
                    
                    # Split box into left and right sub-boxes
                    final_boxes.append((x, y, split_col, h))
                    final_boxes.append((x + split_col, y, w - split_col, h))
                else:
                    final_boxes.append(box)
            else:
                final_boxes.append(box)
                
        # Re-sort boxes after splitting
        final_boxes = sorted(final_boxes, key=lambda b: b[0])
        
        segmented_chars = []
        if not final_boxes:
            return [], img

        # Compute horizontal gaps between adjacent boxes
        gaps = []
        for i in range(1, len(final_boxes)):
            gap = final_boxes[i][0] - (final_boxes[i-1][0] + final_boxes[i-1][2])
            gaps.append(max(0, gap))
            
        median_gap = np.median(gaps) if gaps else 0
        
        # Threshold for detecting spaces (a space is usually wider than characters gaps)
        space_threshold = max(14, 1.7 * median_gap) if median_gap > 0 else 18
        
        annotated_img = img.copy()
        
        for idx, box in enumerate(final_boxes):
            x, y, w, h = box
            
            # Slice character from binary thresholded image (provides clean high-contrast input)
            char_roi = thresh[y:y+h, x:x+w]
            
            # Pad and resize to exactly 28x28 (standard input for MNIST/EMNIST models)
            char_img_28 = OpenCVSegmenter.pad_and_resize(char_roi, 28)
            
            # Append details
            segmented_chars.append({
                'id': idx,
                'x': int(x),
                'y': int(y),
                'w': int(w),
                'h': int(h),
                'char_image': char_img_28,
                'is_space': False
            })
            
            # Draw green bounding box around recognized character
            cv2.rectangle(annotated_img, (x, y), (x+w, y+h), (46, 213, 115), 2) # Light green
            cv2.putText(
                annotated_img, str(idx), (x, y - 6), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 71, 87), 1, cv2.LINE_AA
            ) # Light red index label
            
            # Check for space after this box
            if idx < len(final_boxes) - 1:
                gap = final_boxes[idx+1][0] - (x + w)
                if gap >= space_threshold:
                    segmented_chars.append({
                        'id': f"space_{idx}",
                        'is_space': True,
                        'x': int(x + w),
                        'y': int(y),
                        'w': int(gap),
                        'h': int(h)
                    })
                    # Draw subtle blue indicator line for space
                    cv2.line(annotated_img, (x + w, y + h // 2), (x + w + gap, y + h // 2), (255, 165, 2), 1)

        return segmented_chars, annotated_img

    @staticmethod
    def pad_and_resize(img, size=28):
        """
        Pads image to square preserving aspect ratio and resizes it to size x size.
        """
        h, w = img.shape
        if h == 0 or w == 0:
            return np.zeros((size, size), dtype=np.uint8)
            
        max_dim = max(h, w)
        top = (max_dim - h) // 2
        bottom = max_dim - h - top
        left = (max_dim - w) // 2
        right = max_dim - w - left
        
        # Pad with black border
        padded = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)
        
        # Add an internal margin of 4 pixels to avoid touching the border edges
        margin = max(2, int(max_dim * 0.12))
        padded = cv2.copyMakeBorder(padded, margin, margin, margin, margin, cv2.BORDER_CONSTANT, value=0)
        
        # Resize to target dimension
        resized = cv2.resize(padded, (size, size), interpolation=cv2.INTER_AREA)
        return resized
