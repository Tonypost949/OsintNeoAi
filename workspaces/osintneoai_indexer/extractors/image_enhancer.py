"""
OsintNeoAi Indexer: OpenCV Image Preprocessing & Enhancement Engine
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\extractors\\image_enhancer.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 7

Applies CLAHE contrast equalization, adaptive Gaussian & Otsu binarization,
deskewing, border cleanup, and automated degradation profiling.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional, Tuple, Union
import cv2
import numpy as np

logger = logging.getLogger("osintneoai.extractors.image_enhancer")


class EnhancementProfile(str, Enum):
    PASSTHROUGH = "passthrough"
    LIGHT = "light"
    STANDARD = "standard"
    DOCUMENT_CLEAN = "standard"
    HEAVY = "heavy"
    AUTO = "auto"


class ImageEnhancer:
    """
    OpenCV-based image preprocessing and enhancement engine.
    Applies CLAHE, adaptive thresholding, deskewing, and noise reduction
    to maximize OCR character recognition rates on degraded, faxed, or skewed scans.
    """

    def __init__(
        self,
        clahe_clip_limit: float = 2.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
        adaptive_block_size: int = 31,
        adaptive_c: int = 10,
        max_deskew_angle: float = 45.0
    ) -> None:
        self.clahe_clip_limit = float(clahe_clip_limit)
        self.clahe_grid_size = clahe_grid_size
        self.adaptive_block_size = int(adaptive_block_size)
        if self.adaptive_block_size % 2 == 0:
            self.adaptive_block_size += 1
        self.adaptive_c = int(adaptive_c)
        self.max_deskew_angle = float(max_deskew_angle)
        self._clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=self.clahe_grid_size
        )

    def enhance(
        self,
        image: np.ndarray,
        profile: EnhancementProfile = EnhancementProfile.STANDARD
    ) -> np.ndarray:
        """
        Applies enhancement pipeline according to selected profile.
        Returns a 3-channel RGB uint8 numpy image compatible with RapidOCR.
        """
        if image is None or image.size == 0:
            return image

        if profile == EnhancementProfile.PASSTHROUGH:
            return self.ensure_rgb(image)

        if profile == EnhancementProfile.AUTO:
            profile = self.detect_optimal_profile(image)

        if profile == EnhancementProfile.LIGHT:
            # Grayscale -> CLAHE -> RGB
            gray = self.ensure_grayscale(image)
            enhanced = self.apply_clahe(gray)
            return self.ensure_rgb(enhanced)

        elif profile == EnhancementProfile.STANDARD:
            # Grayscale -> CLAHE -> Deskew -> RGB
            gray = self.ensure_grayscale(image)
            enhanced = self.apply_clahe(gray)
            angle = self.detect_skew_angle(enhanced)
            if abs(angle) > 0.5:
                enhanced = self.deskew(enhanced, angle)
            return self.ensure_rgb(enhanced)

        elif profile == EnhancementProfile.HEAVY:
            # Grayscale -> Remove margins -> Median Denoise -> CLAHE -> Deskew -> Adaptive Gaussian -> RGB
            gray = self.ensure_grayscale(image)
            clean_gray = self.remove_black_margins(gray)
            denoised = cv2.medianBlur(clean_gray, 3)
            enhanced = self.apply_clahe(denoised)
            angle = self.detect_skew_angle(enhanced)
            if abs(angle) > 0.5:
                enhanced = self.deskew(enhanced, angle)
            thresh = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                self.adaptive_block_size,
                self.adaptive_c
            )
            # Remove isolated speckles with opening
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            return self.ensure_rgb(cleaned)

        return self.ensure_rgb(image)

    def apply_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        """Applies Contrast Limited Adaptive Histogram Equalization."""
        gray = self.ensure_grayscale(gray_image)
        return self._clahe.apply(gray)

    def apply_otsu_threshold(self, gray_image: np.ndarray) -> np.ndarray:
        """Applies Otsu's optimal global binarization."""
        gray = self.ensure_grayscale(gray_image)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def apply_adaptive_gaussian_threshold(
        self,
        gray_image: np.ndarray,
        block_size: Optional[int] = None,
        c: Optional[int] = None
    ) -> np.ndarray:
        """Applies local adaptive Gaussian thresholding."""
        gray = self.ensure_grayscale(gray_image)
        bs = block_size or self.adaptive_block_size
        c_val = c if c is not None else self.adaptive_c
        if bs % 2 == 0:
            bs += 1
        if bs < 3:
            bs = 3
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bs, c_val
        )

    def detect_skew_angle(self, gray_image: np.ndarray) -> float:
        """
        Detects skew angle of document text using minimum bounding box of thresholded contours.
        Returns angle in degrees (-45.0 to +45.0).
        """
        try:
            gray = self.ensure_grayscale(gray_image)
            h, w = gray.shape[:2]
            if h < 10 or w < 10:
                return 0.0

            # Invert so text is white on black background
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
            )
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 50:
                return 0.0

            # cv2.minAreaRect takes points in (x, y) coordinates
            points = np.fliplr(coords)
            rect = cv2.minAreaRect(points)
            angle = rect[-1]

            # OpenCV minAreaRect returns angle in range [-90, 0) or [0, 90) depending on version
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = -(angle - 90)
            else:
                angle = -angle

            if abs(angle) > self.max_deskew_angle:
                return 0.0
            return float(angle)
        except Exception as e:
            logger.debug(f"Skew detection error: {e}")
            return 0.0

    def deskew(
        self,
        image: np.ndarray,
        angle: float,
        border_value: Union[int, Tuple[int, int, int]] = 255
    ) -> np.ndarray:
        """Rotates image around its center by angle degrees with white background border."""
        if abs(angle) < 0.2:
            return image
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(
            image,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=border_value
        )
        return deskewed

    def remove_black_margins(self, gray_image: np.ndarray, margin_thresh: int = 30) -> np.ndarray:
        """Cleans dark scanning margins by finding the document content region."""
        gray = self.ensure_grayscale(gray_image)
        h, w = gray.shape[:2]
        if h < 20 or w < 20:
            return gray

        _, binary = cv2.threshold(gray, margin_thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return gray

        largest = max(contours, key=cv2.contourArea)
        x, y, cw, ch = cv2.boundingRect(largest)
        # If bounding rect occupies > 50% of page, mask outside region with white
        if (cw * ch) > (0.50 * w * h):
            mask = np.full((h, w), 255, dtype=np.uint8)
            mask[y:y+ch, x:x+cw] = gray[y:y+ch, x:x+cw]
            return mask
        return gray

    def detect_optimal_profile(self, image: np.ndarray) -> EnhancementProfile:
        """
        Heuristic evaluator assessing contrast (std dev of intensities) and sharpness (Laplacian variance).
        """
        gray = self.ensure_grayscale(image)
        std_dev = float(np.std(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Low standard deviation indicates low contrast scan; low variance indicates blurry scan
        if std_dev < 35.0 or laplacian_var < 50.0:
            return EnhancementProfile.HEAVY
        elif std_dev < 55.0 or laplacian_var < 150.0:
            return EnhancementProfile.STANDARD
        else:
            return EnhancementProfile.LIGHT

    @staticmethod
    def ensure_grayscale(image: np.ndarray) -> np.ndarray:
        """Converts any image format to single-channel 8-bit grayscale."""
        if len(image.shape) == 2:
            return image
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                return cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
            elif image.shape[2] == 3:
                return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image

    @staticmethod
    def ensure_rgb(image: np.ndarray) -> np.ndarray:
        """Converts any image format to 3-channel 8-bit RGB."""
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 1:
                return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return image
