# Milestone 2 (M2) Deep Text Extraction & OCR Engine: Architectural Specification & Blueprint

**Module**: `workspaces.osintneoai_indexer.extractors`  
**Working Directory**: `C:\OsintNeoAi\.agents\explorer_m2_1`  
**Timestamp**: 2026-08-29T17:55:00Z  
**Author**: Explorer Agent M2-1  
**Target Milestone**: Milestone 2 (M2: Deep Text Extraction & OCR Engine)  
**Dependencies**: Milestone 1 Deliverables (`config.py`, `storage.hasher`, `connectors`)

---

## 1. Executive Summary & Architectural Overview

Milestone 2 (M2) delivers the core extraction and normalization engines for the OsintNeoAi Indexer pipeline, implementing Features 5–11 from `PROJECT.md`:
1. **Feature 5**: Native Digital Text Extraction (PyMuPDF high-speed parser with block-level layout analysis).
2. **Feature 6**: Neural Offline OCR Engine (CPU-optimized RapidOCR ONNX runtime integration with lazy model initialization, multi-page generator, and bounding box spatial sorting).
3. **Feature 7**: Image Preprocessing & Enhancement (OpenCV CLAHE contrast equalization, adaptive Otsu/Gaussian thresholding, deskewing, and noise reduction for degraded/faxed scans).
4. **Features 8–11**: Multi-Tier Normalization Pipeline (ISO 8601 timestamps, dual float/cents financial transactions, federal/state case dockets, and correspondence metadata).

### Core Extraction Architecture & Data Flow

```
                                  [ IngestedArtifact ]
                               (from M1 Ingestion Stream)
                                           │
                                           ▼
                            [ DocumentExtractor.extract() ]
                                           │
         ┌─────────────────────────────────┴─────────────────────────────────┐
         │                                                                   │
         ▼ (application/pdf)                                                 ▼ (Non-PDF Formats)
  [ PyMuPDF Document ]                                        ┌──────────────────────────────┐
         │                                                    │ Tier 5: Dedicated Parsers    │
         ▼ (per page)                                         ├──────────────────────────────┤
  ┌──────────────────────────────────────────────┐            │ • DOCX: python-docx parser   │
  │ Tier 1: Digital Text (page.get_text())       │            │ • HTML: HTMLTextExtractor    │
  └──────────────────────┬───────────────────────┘            │ • Email: MailboxReader / EML │
                         │                                    │ • Text/JSON/CSV: UTF-8 Stream│
                         ▼                                    └──────────────┬───────────────┘
  ┌──────────────────────────────────────────────┐                           │
  │ Tier 2: Density & Glyph Quality Heuristic    │                           │
  │ (chars >= 40 & printable_ratio >= 0.85 &     │                           │
  │  valid glyph sequences?)                     │                           │
  └──────────────┬───────────────────────────────┘                           │
                 │                                                           │
        ┌────────┴────────┐                                                  │
        │ PASS            │ FAIL (Scanned/Degraded)                          │
        ▼                 ▼                                                  │
  [ Digital Text ]  ┌──────────────────────────────────────────────┐         │
                    │ Tier 3: 300 DPI Rendering + RapidOCR ONNX    │         │
                    │ (page.get_pixmap(dpi=300) -> RapidOCR)       │         │
                    └──────────────────────┬───────────────────────┘         │
                                           │                                 │
                                  ┌────────┴────────┐                        │
                                  │ Confidence>=0.65│ Confidence < 0.65      │
                                  │ & lines > 0     │ or lines == 0          │
                                  ▼                 ▼                        │
                            [ RapidOCR Text ] ┌────────────────────────┐     │
                                              │ Tier 4: OpenCV CLAHE   │     │
                                              │ + Adaptive Gaussian    │     │
                                              │ + Deskewing            │     │
                                              │ + 2nd-Pass RapidOCR    │     │
                                              └────────────┬───────────┘     │
                                                           │                 │
                                                           ▼                 │
                                                    [ Enhanced Text ]        │
                                                           │                 │
                                                           ▼                 │
                                              ┌────────────────────────┐     │
                                              │ Free Memory:           │     │
                                              │ del pix; del img_np    │     │
                                              │ gc.collect() (every 10)│     │
                                              └────────────┬───────────┘     │
                                                           │                 │
                                                           ▼                 │
                                              [ Page / Document Text Body ]  │
                                                           │                 │
         ┌─────────────────────────────────────────────────┴─────────────────┘
         ▼
  [ Multi-Tier Normalization Pipeline ]
  ├── 1. Date Normalizer -> ISO 8601 UTC (YYYY-MM-DD / YYYY-MM-DDTHH:MM:SSZ)
  ├── 2. Financial Normalizer -> Float + Integer Cents ($320M -> 32000000000)
  ├── 3. Case Docket Normalizer -> Federal (8:23-cr-00108) & CA (30-2021-01201327)
  └── 4. Entity & Header Normalizer -> FROM/TO/ATTN extraction, honorific stripping
         │
         ▼
  [ ExtractedRecord ] ──> Handed off to Milestone 3 (Entity Resolution & Vault DB)
```

---

## 2. Module 1 Specification: `extractors/ocr_engine.py`

### 2.1 Design Objectives & Invariants
- **Lazy Initialization**: RapidOCR ONNX models (DBNet text detector, SVTR/CRNN recognizer, angle classifier) must NOT be loaded on module import. Models are initialized on the first OCR request or via explicit `warmup()`.
- **Strict Memory Management**: Every rendered pixmap and numpy array must be deallocated immediately with explicit `del pix; del img_np`. Periodic `gc.collect()` is triggered every 10 pages to ensure RSS memory stays under 250 MB.
- **Bounding Box & Spatial Reading Order**: Bounding box coordinates are preserved for each text line and sorted in top-to-bottom, left-to-right reading order with multi-column support.
- **Confidence Filtering**: Lines with confidence scores below a configurable threshold (e.g. 0.30) are filtered to remove phantom OCR artifacts.

### 2.2 Data Classes & Type Signatures

```python
from __future__ import annotations

import gc
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Dict, Generator, Iterable, List, Optional, Sequence, Tuple, Union
import numpy as np

logger = logging.getLogger("osintneoai.extractors.ocr_engine")

@dataclass(frozen=True)
class OCRPoint:
    x: float
    y: float

@dataclass(frozen=True)
class OCRLine:
    """
    Immutable representation of an individual OCR-detected text line.
    """
    text: str
    confidence: float
    box: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    
    @property
    def top_left(self) -> Tuple[float, float]:
        return self.box[0]
        
    @property
    def bottom_right(self) -> Tuple[float, float]:
        return self.box[2]
        
    @property
    def width(self) -> float:
        return abs(self.box[1][0] - self.box[0][0])
        
    @property
    def height(self) -> float:
        return abs(self.box[2][1] - self.box[1][1])
        
    @property
    def center_y(self) -> float:
        return (self.box[0][1] + self.box[2][1]) / 2.0

@dataclass(frozen=True)
class OCRPageResult:
    """
    Structured result for a single page OCR run.
    """
    page_number: int
    full_text: str
    lines: Tuple[OCRLine, ...]
    avg_confidence: float
    detection_time_sec: float
    recognition_time_sec: float
    total_time_sec: float
    width: int
    height: int
```

### 2.3 `OCREngine` Class Implementation Blueprint

```python
class OCREngine:
    """
    High-accuracy, CPU-optimized Neural OCR engine wrapping RapidOCR ONNX.
    Features lazy loading, spatial line sorting, confidence filtering, and strict memory safety.
    """

    _instance: Optional[OCREngine] = None

    def __init__(
        self,
        min_confidence: float = 0.30,
        det_use_cuda: bool = False,
        rec_use_cuda: bool = False,
        cls_use_cuda: bool = False,
    ) -> None:
        self.min_confidence = min_confidence
        self.det_use_cuda = det_use_cuda
        self.rec_use_cuda = rec_use_cuda
        self.cls_use_cuda = cls_use_cuda
        self._engine: Optional[Any] = None
        self._is_initialized: bool = False

    @classmethod
    def get_instance(cls, min_confidence: float = 0.30) -> OCREngine:
        """Singleton accessor to reuse loaded ONNX sessions across extractor passes."""
        if cls._instance is None:
            cls._instance = cls(min_confidence=min_confidence)
        return cls._instance

    def warmup(self) -> None:
        """Explicitly load ONNX models into memory."""
        if not self._is_initialized:
            self._get_engine()

    def _get_engine(self) -> Any:
        """Lazy loader for RapidOCR ONNX instance."""
        if self._engine is None:
            logger.info("Initializing RapidOCR ONNX Runtime engine...")
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
            self._is_initialized = True
            logger.info("RapidOCR ONNX Runtime engine successfully initialized.")
        return self._engine

    def ocr_image(
        self,
        image_input: Union[np.ndarray, bytes, str, Path],
        min_confidence: Optional[float] = None,
        page_number: int = 1
    ) -> OCRPageResult:
        """
        Executes OCR on an image array, raw bytes, or disk path.
        """
        engine = self._get_engine()
        min_conf = min_confidence if min_confidence is not None else self.min_confidence

        # Format input as numpy ndarray
        img_np, should_cleanup = self._prepare_image_array(image_input)
        
        try:
            h, w = img_np.shape[:2]
            
            # Execute RapidOCR inference
            # RapidOCR returns (results, elapse_list) or None
            raw_results, elapse = engine(img_np)
            
            det_time = float(elapse[0]) if elapse and len(elapse) > 0 else 0.0
            rec_time = float(elapse[2]) if elapse and len(elapse) > 2 else 0.0
            total_time = sum(elapse) if elapse else 0.0
            
            if not raw_results:
                return OCRPageResult(
                    page_number=page_number,
                    full_text="",
                    lines=(),
                    avg_confidence=0.0,
                    detection_time_sec=det_time,
                    recognition_time_sec=rec_time,
                    total_time_sec=total_time,
                    width=w,
                    height=h
                )
                
            parsed_lines: List[OCRLine] = []
            total_conf = 0.0
            
            for item in raw_results:
                # item: [box_points, text, confidence_str_or_float]
                raw_box = item[0]
                text = str(item[1]).strip()
                conf = float(item[2])
                
                if conf < min_conf or not text:
                    continue
                    
                box_tuple = tuple(tuple(float(c) for c in pt) for pt in raw_box)
                line = OCRLine(
                    text=text,
                    confidence=round(conf, 4),
                    box=box_tuple  # type: ignore
                )
                parsed_lines.append(line)
                total_conf += conf
                
            # Sort lines in natural reading order (top-to-bottom, left-to-right)
            sorted_lines = self._sort_reading_order(parsed_lines)
            full_text = "\n".join([line.text for line in sorted_lines])
            avg_conf = (total_conf / len(parsed_lines)) if parsed_lines else 0.0
            
            return OCRPageResult(
                page_number=page_number,
                full_text=full_text,
                lines=tuple(sorted_lines),
                avg_confidence=round(avg_conf, 4),
                detection_time_sec=round(det_time, 4),
                recognition_time_sec=round(rec_time, 4),
                total_time_sec=round(total_time, 4),
                width=w,
                height=h
            )
        finally:
            if should_cleanup:
                del img_np

    def _prepare_image_array(
        self,
        image_input: Union[np.ndarray, bytes, str, Path]
    ) -> Tuple[np.ndarray, bool]:
        """Converts heterogeneous image inputs to a normalized 3-channel BGR/RGB numpy array."""
        import cv2
        if isinstance(image_input, np.ndarray):
            img = image_input
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            return img, False
        elif isinstance(image_input, (bytes, bytearray)):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image bytes with cv2.imdecode")
            return img, True
        elif isinstance(image_input, (str, Path)):
            path_str = str(image_input)
            img = cv2.imread(path_str, cv2.IMREAD_COLOR)
            if img is None:
                raise FileNotFoundError(f"Image not found or unreadable: {path_str}")
            return img, True
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def _sort_reading_order(self, lines: List[OCRLine], line_margin: float = 12.0) -> List[OCRLine]:
        """
        Sorts OCR lines in spatial reading order.
        Groups lines with similar vertical centers into horizontal bands, then sorts left-to-right.
        """
        if not lines:
            return []
            
        # Primary sort by Y
        sorted_by_y = sorted(lines, key=lambda l: l.center_y)
        
        bands: List[List[OCRLine]] = []
        current_band: List[OCRLine] = []
        current_band_y = sorted_by_y[0].center_y
        
        for line in sorted_by_y:
            if abs(line.center_y - current_band_y) <= line_margin:
                current_band.append(line)
            else:
                bands.append(sorted(current_band, key=lambda l: l.top_left[0]))
                current_band = [line]
                current_band_y = line.center_y
                
        if current_band:
            bands.append(sorted(current_band, key=lambda l: l.top_left[0]))
            
        flattened: List[OCRLine] = []
        for band in bands:
            flattened.extend(band)
        return flattened

    def ocr_pdf_stream(
        self,
        pdf_stream: Union[BinaryIO, bytes, Path, str],
        dpi: int = 300,
        min_confidence: Optional[float] = None,
        max_pages: Optional[int] = None
    ) -> Generator[OCRPageResult, None, None]:
        """
        Memory-bounded multi-page PDF OCR generator.
        Renders pages at 300 DPI, processes OCR, destroys pixmaps/numpy arrays,
        and triggers garbage collection every 10 pages.
        """
        import pymupdf
        import cv2
        
        if isinstance(pdf_stream, (str, Path)):
            doc = pymupdf.open(str(pdf_stream))
        elif isinstance(pdf_stream, (bytes, bytearray)):
            doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
        else:
            pdf_bytes = pdf_stream.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
        try:
            total_pages = len(doc)
            limit = min(total_pages, max_pages) if max_pages else total_pages
            
            for page_idx in range(limit):
                page = doc[page_idx]
                pix = page.get_pixmap(dpi=dpi)
                
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                if pix.n == 4:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
                    
                # Explicitly destroy C-level pixmap
                del pix
                
                result = self.ocr_image(img_np, min_confidence=min_confidence, page_number=page_idx + 1)
                
                # Explicitly destroy numpy image buffer
                del img_np
                
                # Periodic GC collection to prevent fragmentation
                if (page_idx + 1) % 10 == 0:
                    gc.collect()
                    
                yield result
        finally:
            doc.close()
            gc.collect()
```

---

## 3. Module 2 Specification: `extractors/image_enhancer.py`

### 3.1 Design Objectives & Invariants
- **CLAHE Contrast Equalization**: Solves low contrast, faded faxes, carbon copies, and yellowed documents via Contrast Limited Adaptive Histogram Equalization (`cv2.createCLAHE`).
- **Adaptive Thresholding**: Binarizes documents with uneven shadows and illumination gradients using `cv2.adaptiveThreshold` (Adaptive Gaussian) and `cv2.threshold` (Otsu).
- **Contour & Hough Deskewing**: Automatically detects skew angles up to $\pm 45^\circ$ using minimum bounding box of text contours and straightens images via `cv2.warpAffine` with high-quality cubic interpolation.
- **Salt-and-Pepper Denoising**: Removes scanner artifacts, black margin borders, and thermal fax noise using median filtering and morphological operations while maintaining character stroke clarity.
- **Non-Destructive Operations**: Image transformations operate on bounded numpy copies and cleanly return transformed images ready for RapidOCR consumption.

### 3.2 Enhancement Profiles & Algorithms

```python
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
    HEAVY = "heavy"
    AUTO = "auto"

class ImageEnhancer:
    """
    OpenCV-based image preprocessing and enhancement engine.
    Applies CLAHE, adaptive thresholding, deskewing, and noise reduction.
    """

    def __init__(
        self,
        clahe_clip_limit: float = 2.0,
        clahe_grid_size: Tuple[int, int] = (8, 8),
        adaptive_block_size: int = 31,
        adaptive_c: int = 10,
        max_deskew_angle: float = 45.0
    ) -> None:
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_grid_size = clahe_grid_size
        self.adaptive_block_size = adaptive_block_size
        self.adaptive_c = adaptive_c
        self.max_deskew_angle = max_deskew_angle
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
        Returns a 3-channel RGB image compatible with RapidOCR.
        """
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
            # Grayscale -> Median Denoise -> CLAHE -> Deskew -> Adaptive Gaussian Threshold -> RGB
            gray = self.ensure_grayscale(image)
            denoised = cv2.medianBlur(gray, 3)
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
        return self._clahe.apply(gray_image)

    def apply_otsu_threshold(self, gray_image: np.ndarray) -> np.ndarray:
        """Applies Otsu's optimal global binarization."""
        _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def apply_adaptive_gaussian_threshold(
        self,
        gray_image: np.ndarray,
        block_size: Optional[int] = None,
        c: Optional[int] = None
    ) -> np.ndarray:
        """Applies local adaptive Gaussian thresholding."""
        bs = block_size or self.adaptive_block_size
        c_val = c if c is not None else self.adaptive_c
        # Block size must be odd and > 1
        if bs % 2 == 0:
            bs += 1
        return cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bs, c_val
        )

    def detect_skew_angle(self, gray_image: np.ndarray) -> float:
        """
        Detects skew angle of document text using minimum bounding box of thresholded contours.
        Returns angle in degrees (-45.0 to +45.0).
        """
        try:
            # Invert so text is white on black background
            thresh = cv2.adaptiveThreshold(
                gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 10
            )
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 50:
                return 0.0
                
            rect = cv2.minAreaRect(coords)
            angle = rect[-1]
            
            # OpenCV minAreaRect returns angle in range [-90, 0)
            if angle < -45:
                angle = -(90 + angle)
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
        """Cleans black scanning margins by finding outer document bounding box."""
        h, w = gray_image.shape[:2]
        _, binary = cv2.threshold(gray_image, margin_thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return gray_image
        largest = max(contours, key=cv2.contourArea)
        x, y, cw, ch = cv2.boundingRect(largest)
        # If bounding rect occupies > 60% of page, mask outside region with white
        if (cw * ch) > (0.60 * w * h):
            mask = np.full((h, w), 255, dtype=np.uint8)
            mask[y:y+ch, x:x+cw] = gray_image[y:y+ch, x:x+cw]
            return mask
        return gray_image

    def detect_optimal_profile(self, image: np.ndarray) -> EnhancementProfile:
        """
        Heuristic evaluator assessing contrast (std dev of intensities) and sharpness (Laplacian variance).
        """
        gray = self.ensure_grayscale(image)
        std_dev = float(np.std(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        # Low standard deviation indicates low contrast scan
        if std_dev < 35.0 or laplacian_var < 50.0:
            return EnhancementProfile.HEAVY
        elif std_dev < 55.0:
            return EnhancementProfile.STANDARD
        else:
            return EnhancementProfile.LIGHT

    @staticmethod
    def ensure_grayscale(image: np.ndarray) -> np.ndarray:
        """Converts any image format to single-channel 8-bit grayscale."""
        if len(image.shape) == 2:
            return image
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def ensure_rgb(image: np.ndarray) -> np.ndarray:
        """Converts any image format to 3-channel 8-bit RGB."""
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        return image
```

---

## 4. Module 3 Specification: `extractors/document_extractor.py` (Core 5-Tier Extraction Ladder)

### 4.1 Design Objectives & Invariants
- **5-Tier Fallback Ladder**:
  - **Tier 1**: High-speed digital PyMuPDF extraction (`page.get_text()`).
  - **Tier 2**: Character density, printable character ratio, and font glyph health validation.
  - **Tier 3**: 300 DPI page pixmap rasterization + RapidOCR ONNX neural text detection.
  - **Tier 4**: OpenCV CLAHE + Adaptive Gaussian thresholding + Deskewing + 2nd-pass RapidOCR.
  - **Tier 5**: Non-PDF dedicated format parsers (DOCX, HTML, Email/MBOX, CSV/JSON/TXT).
- **Interface Contract Compliance**:
  - Accepts `IngestedArtifact` from M1.
  - Generates `ExtractedRecord` matching the exact `PROJECT.md` M2 ↔ M3 specification.
- **Zero Memory Leaks**: Streamlined generator interface supporting multi-hundred page filings without cumulative RAM buildup.

### 4.2 Class Architecture & Implementation Blueprint

```python
from __future__ import annotations

import email
import gc
import html
import io
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, Generator, List, Optional, Sequence, Tuple, Union

import pymupdf
import numpy as np

from workspaces.osintneoai_indexer.config import (
    FileCategory,
    IndexerConfig,
    MIN_DIGITAL_TEXT_DENSITY,
    OCR_CONFIDENCE_THRESHOLD,
    OCR_DPI,
    get_file_category,
    get_mime_type,
)
from workspaces.osintneoai_indexer.connectors.local_crawler import IngestedArtifact
from workspaces.osintneoai_indexer.extractors.ocr_engine import OCREngine, OCRPageResult
from workspaces.osintneoai_indexer.extractors.image_enhancer import EnhancementProfile, ImageEnhancer

logger = logging.getLogger("osintneoai.extractors.document_extractor")

# ==============================================================================
# 1. Interface Contracts (PROJECT.md M2 ↔ M3)
# ==============================================================================

@dataclass
class ExtractedRecord:
    """
    Canonical extracted artifact record passed from M2 to M3.
    """
    record_id: str               # Deterministic artifact-derived ID or UUID
    artifact_sha256: str         # SHA-256 hex string of raw file
    source_path: str             # Source URI or local file path
    source_type: str             # 'local_file', 'gdrive', 'mailbox', 'archive_member'
    mime_type: str               # Canonical MIME type (e.g. application/pdf)
    normalized_date: Optional[str] # ISO 8601 UTC date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
    raw_date_string: Optional[str] # Unparsed raw date text
    extracted_text: str          # Full normalized text body
    ocr_engine_used: str         # 'pymupdf_native', 'rapidocr_onnx', 'rapidocr_enhanced', 'docx_parser', 'html_parser', 'email_parser', 'raw_text'
    financial_amounts: List[Dict[str, Any]] # [{"amount_raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}]
    case_numbers: List[str]      # ["8:23-cr-00108-CJC", "30-2021-01201327-CL-UD-CJC"]
    sender: Optional[str]
    recipients: List[str]
    metadata: Dict[str, Any]

@dataclass
class PageExtractionResult:
    """
    Internal page-level extraction telemetry container.
    """
    page_number: int
    text: str
    extraction_tier: str         # 'tier1_digital', 'tier3_ocr', 'tier4_enhanced_ocr'
    confidence: float
    char_count: int
    printable_ratio: float
    elapse_seconds: float

# ==============================================================================
# 2. HTML & Plaintext Helper Parsers
# ==============================================================================

class HTMLTextExtractor(HTMLParser):
    """
    Lightweight, robust HTML text extractor using standard library html.parser.
    Strips scripts/styles, extracts title, meta description, and clean paragraphs.
    """
    def __init__(self) -> None:
        super().__init__()
        self.fed: List[str] = []
        self.title: Optional[str] = None
        self._in_title: bool = False
        self._in_script_or_style: bool = False
        self.meta_tags: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "noscript"):
            self._in_script_or_style = True
        elif tag_lower == "title":
            self._in_title = True
        elif tag_lower == "meta":
            attr_dict = {k.lower(): (v or "") for k, v in attrs}
            name = attr_dict.get("name", attr_dict.get("property", ""))
            content = attr_dict.get("content", "")
            if name and content:
                self.meta_tags[name] = content
        elif tag_lower in ("p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self.fed.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "noscript"):
            self._in_script_or_style = False
        elif tag_lower == "title":
            self._in_title = False
        elif tag_lower in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self.fed.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._in_script_or_style:
            cleaned = data.strip()
            if cleaned:
                if self._in_title and not self.title:
                    self.title = cleaned
                self.fed.append(data)

    def get_text(self) -> str:
        raw = "".join(self.fed)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.split("\n")]
        return "\n".join([line for line in lines if line])

# ==============================================================================
# 3. DocumentExtractor Core Class
# ==============================================================================

class DocumentExtractor:
    """
    Core Extraction Ladder Orchestrator implementing the 5-tier fallback engine.
    """

    def __init__(
        self,
        config: Optional[IndexerConfig] = None,
        ocr_engine: Optional[OCREngine] = None,
        image_enhancer: Optional[ImageEnhancer] = None,
    ) -> None:
        self.config = config or IndexerConfig.default()
        self.ocr_engine = ocr_engine or OCREngine.get_instance(
            min_confidence=self.config.ocr_confidence_threshold
        )
        self.image_enhancer = image_enhancer or ImageEnhancer(
            clahe_clip_limit=self.config.ocr_confidence_threshold
        )

    def extract(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """
        Main entrypoint: ingests IngestedArtifact, executes 5-tier extraction,
        runs multi-tier normalizers, and returns canonical ExtractedRecord.
        """
        category = get_file_category(artifact.mime_type)
        stream_factory = artifact.raw_stream_factory

        if category == FileCategory.PDF:
            return self._extract_pdf(artifact)
        elif category == FileCategory.IMAGE:
            return self._extract_image(artifact)
        elif category == FileCategory.DOCX:
            return self._extract_docx(artifact)
        elif category == FileCategory.HTML:
            return self._extract_html(artifact)
        elif category == FileCategory.EMAIL:
            return self._extract_email(artifact)
        elif category in (FileCategory.TEXT, FileCategory.TABULAR):
            return self._extract_text(artifact)
        else:
            # Fallback raw byte extraction
            return self._extract_fallback(artifact)

    def _extract_pdf(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """
        Processes PDF via Tiers 1-4 page-by-page generator with strict memory destruction.
        """
        import cv2
        
        stream = artifact.raw_stream_factory()
        try:
            pdf_bytes = stream.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        finally:
            stream.close()
            
        page_results: List[PageExtractionResult] = []
        methods_used: Set[str] = set()
        total_conf = 0.0
        
        try:
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                
                # --- TIER 1: PyMuPDF Native Text Extraction ---
                native_text = page.get_text("text").strip()
                printable_chars = len([c for c in native_text if c.isprintable() and not c.isspace()])
                total_chars = len(native_text)
                printable_ratio = (printable_chars / total_chars) if total_chars > 0 else 0.0
                
                # --- TIER 2: Density & Glyph Quality Heuristic ---
                if printable_chars >= self.config.min_digital_text_density and printable_ratio >= 0.85:
                    page_results.append(PageExtractionResult(
                        page_number=page_idx + 1,
                        text=native_text,
                        extraction_tier="tier1_digital",
                        confidence=1.0,
                        char_count=total_chars,
                        printable_ratio=printable_ratio,
                        elapse_seconds=0.001
                    ))
                    methods_used.add("pymupdf_native")
                    total_conf += 1.0
                else:
                    # --- TIER 3: 300 DPI Rendering + RapidOCR ---
                    pix = page.get_pixmap(dpi=self.config.ocr_dpi)
                    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                    if pix.n == 4:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
                    elif pix.n == 1:
                        img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
                    
                    # Delete pixmap immediately
                    del pix
                    
                    ocr_res = self.ocr_engine.ocr_image(img_np, page_number=page_idx + 1)
                    
                    # --- TIER 4: OpenCV CLAHE & Preprocessing (if Tier 3 is weak) ---
                    if (not ocr_res.lines or ocr_res.avg_confidence < self.config.ocr_confidence_threshold):
                        enhanced_img = self.image_enhancer.enhance(img_np, profile=EnhancementProfile.HEAVY)
                        enhanced_ocr_res = self.ocr_engine.ocr_image(enhanced_img, page_number=page_idx + 1)
                        
                        # Compare whether enhanced pass extracted more characters / higher confidence
                        if len(enhanced_ocr_res.full_text) > len(ocr_res.full_text) or enhanced_ocr_res.avg_confidence > ocr_res.avg_confidence:
                            ocr_res = enhanced_ocr_res
                            methods_used.add("rapidocr_enhanced")
                        else:
                            methods_used.add("rapidocr_onnx")
                        del enhanced_img
                    else:
                        methods_used.add("rapidocr_onnx")
                        
                    # Delete numpy image array immediately
                    del img_np
                    
                    page_results.append(PageExtractionResult(
                        page_number=page_idx + 1,
                        text=ocr_res.full_text,
                        extraction_tier="tier4_enhanced_ocr" if "rapidocr_enhanced" in methods_used else "tier3_ocr",
                        confidence=ocr_res.avg_confidence,
                        char_count=len(ocr_res.full_text),
                        printable_ratio=1.0 if ocr_res.full_text else 0.0,
                        elapse_seconds=ocr_res.total_time_sec
                    ))
                    total_conf += ocr_res.avg_confidence
                    
                # Garbage collection every 10 pages
                if (page_idx + 1) % 10 == 0:
                    gc.collect()
        finally:
            doc.close()
            gc.collect()

        combined_text = "\n\n--- [Page %d] ---\n".join([f"--- [Page {p.page_number}] ---\n" + p.text for p in page_results])
        full_text = "\n\n".join([f"--- [Page {p.page_number}] ---\n{p.text}" for p in page_results])
        avg_doc_conf = (total_conf / len(page_results)) if page_results else 0.0
        primary_method = "+".join(sorted(methods_used)) if methods_used else "pymupdf_native"

        # Apply multi-tier normalizers to full document text
        return self._build_extracted_record(
            artifact=artifact,
            text_body=full_text,
            ocr_engine_used=primary_method,
            page_count=len(page_results),
            avg_confidence=round(avg_doc_conf, 4),
            metadata={"pages": [p.__dict__ for p in page_results]}
        )

    def _extract_image(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Executes OCR directly on image files with OpenCV enhancement fallback."""
        stream = artifact.raw_stream_factory()
        try:
            img_bytes = stream.read()
        finally:
            stream.close()
            
        ocr_res = self.ocr_engine.ocr_image(img_bytes, page_number=1)
        method = "rapidocr_onnx"
        
        if not ocr_res.lines or ocr_res.avg_confidence < self.config.ocr_confidence_threshold:
            # Decode to numpy array and enhance
            import cv2
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_np is not None:
                enhanced = self.image_enhancer.enhance(img_np, profile=EnhancementProfile.HEAVY)
                enhanced_res = self.ocr_engine.ocr_image(enhanced, page_number=1)
                if len(enhanced_res.full_text) > len(ocr_res.full_text) or enhanced_res.avg_confidence > ocr_res.avg_confidence:
                    ocr_res = enhanced_res
                    method = "rapidocr_enhanced"
                del img_np
                del enhanced

        return self._build_extracted_record(
            artifact=artifact,
            text_body=ocr_res.full_text,
            ocr_engine_used=method,
            page_count=1,
            avg_confidence=ocr_res.avg_confidence,
            metadata={"detection_time": ocr_res.detection_time_sec, "recognition_time": ocr_res.recognition_time_sec}
        )

    def _extract_docx(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text, tables, and document properties from DOCX files."""
        import docx
        stream = artifact.raw_stream_factory()
        try:
            doc_file = docx.Document(stream)
            paragraphs = [p.text for p in doc_file.paragraphs if p.text.strip()]
            for table in doc_file.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                    if row_text:
                        paragraphs.append(row_text)
            text_body = "\n".join(paragraphs)
            
            # Extract docx core metadata
            core_props = {}
            if hasattr(doc_file, "core_properties"):
                props = doc_file.core_properties
                if props.author: core_props["author"] = props.author
                if props.title: core_props["title"] = props.title
                if props.created: core_props["created"] = props.created.isoformat()
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body,
            ocr_engine_used="docx_parser",
            page_count=1,
            avg_confidence=1.0,
            metadata=core_props
        )

    def _extract_html(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text body and meta tags from HTML documents."""
        stream = artifact.raw_stream_factory()
        try:
            html_content = stream.read().decode("utf-8", errors="replace")
        finally:
            stream.close()
            
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        text_body = parser.get_text()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body,
            ocr_engine_used="html_parser",
            page_count=1,
            avg_confidence=1.0,
            metadata={"title": parser.title, "meta_tags": parser.meta_tags}
        )

    def _extract_email(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts email headers, sender/recipient, subject, and message body from EML/MBOX."""
        stream = artifact.raw_stream_factory()
        try:
            msg = email.message_from_binary_file(stream)
        finally:
            stream.close()
            
        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
                elif ctype == "text/html" and not body_parts:
                    payload = part.get_payload(decode=True)
                    if payload:
                        p = HTMLTextExtractor()
                        p.feed(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
                        body_parts.append(p.get_text())
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_parts.append(payload.decode(msg.get_content_charset() or "utf-8", errors="replace"))
                
        text_body = "\n".join(body_parts)
        headers = {
            "From": msg.get("From"),
            "To": msg.get("To"),
            "Subject": msg.get("Subject"),
            "Date": msg.get("Date"),
            "Message-ID": msg.get("Message-ID")
        }

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body,
            ocr_engine_used="email_parser",
            page_count=1,
            avg_confidence=1.0,
            metadata=headers
        )

    def _extract_text(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text from plain text, markdown, CSV, or JSON artifacts."""
        stream = artifact.raw_stream_factory()
        try:
            raw_bytes = stream.read()
            text_body = raw_bytes.decode("utf-8", errors="replace")
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body,
            ocr_engine_used="raw_text",
            page_count=1,
            avg_confidence=1.0,
            metadata={}
        )

    def _extract_fallback(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Fallback extractor for unmapped binary formats."""
        stream = artifact.raw_stream_factory()
        try:
            raw_bytes = stream.read(1024 * 1024) # Read first 1MB
            text_body = "".join([chr(b) if 32 <= b <= 126 or b in (10, 13, 9) else " " for b in raw_bytes])
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body.strip(),
            ocr_engine_used="binary_strings",
            page_count=1,
            avg_confidence=0.5,
            metadata={"status": "fallback_binary_dump"}
        )

    def _build_extracted_record(
        self,
        artifact: IngestedArtifact,
        text_body: str,
        ocr_engine_used: str,
        page_count: int,
        avg_confidence: float,
        metadata: Dict[str, Any]
    ) -> ExtractedRecord:
        """
        Executes date, financial, case docket, and correspondence normalization
        to build the canonical ExtractedRecord for Milestone 3.
        """
        from workspaces.osintneoai_indexer.normalizers.date_normalizer import normalize_dates_from_text
        from workspaces.osintneoai_indexer.normalizers.financial_normalizer import extract_financial_amounts
        from workspaces.osintneoai_indexer.normalizers.case_normalizer import extract_case_numbers
        from workspaces.osintneoai_indexer.normalizers.entity_normalizer import extract_correspondence_parties

        # 1. Date normalization
        norm_date, raw_date = normalize_dates_from_text(text_body, artifact.metadata)
        
        # 2. Financial amounts normalization
        financials = extract_financial_amounts(text_body)
        
        # 3. Legal case identifiers & court citations
        case_nums = extract_case_numbers(text_body)
        
        # 4. Sender and recipients metadata
        sender, recipients = extract_correspondence_parties(text_body, metadata)

        # Merge metadata
        merged_meta = dict(artifact.metadata or {})
        merged_meta.update(metadata)
        merged_meta["page_count"] = page_count
        merged_meta["avg_confidence"] = avg_confidence

        return ExtractedRecord(
            record_id=f"rec_{artifact.artifact_id[:16]}",
            artifact_sha256=artifact.artifact_id,
            source_path=artifact.source_uri,
            source_type=self._determine_source_type(artifact.source_uri),
            mime_type=artifact.mime_type,
            normalized_date=norm_date,
            raw_date_string=raw_date,
            extracted_text=text_body,
            ocr_engine_used=ocr_engine_used,
            financial_amounts=financials,
            case_numbers=case_nums,
            sender=sender,
            recipients=recipients,
            metadata=merged_meta
        )

    def _determine_source_type(self, source_uri: str) -> str:
        if source_uri.startswith("http://") or source_uri.startswith("https://") or "drive.google.com" in source_uri:
            return "gdrive"
        elif "zip://" in source_uri or "tar://" in source_uri:
            return "archive_member"
        elif source_uri.endswith(".mbox") or source_uri.endswith(".eml"):
            return "mailbox"
        return "local_file"
```

---

## 5. Multi-Tier Normalization Specifications (Features 8–11)

### 5.1 Date Normalizer: `normalizers/date_normalizer.py` (Feature 8)
- **Target Invariant**: Parses timestamps from legal filings, city resolutions, emails, and court stamps into strict canonical ISO 8601 UTC strings (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).
- **Algorithm**:
  1. Regex scanner for court filing stamps: `FILED \d{1,2}/\d{1,2}/\d{4}`, `ENTERED \d{1,2}/\d{1,2}/\d{4}`, `DATED this \d{1,2}(?:st|nd|rd|th)? day of [A-Za-z]+, \d{4}`.
  2. US Date precedence: `dayfirst=False` in `dateutil.parser` ensuring `06/29/2021` parses to `2021-06-29` (Woodbridge Meadows Triple Default Judgment).
  3. Timezone conversion: naive timestamps cast to UTC; non-UTC offsets converted to `Z`.
  4. Fallback hierarchy: (a) Header/stamp date $\rightarrow$ (b) Earliest mentioned in-text date $\rightarrow$ (c) File modification date $\rightarrow$ (d) Current UTC timestamp.

### 5.2 Financial Normalizer: `normalizers/financial_normalizer.py` (Feature 9)
- **Target Invariant**: Resolves financial amounts without floating-point precision loss, returning both float and exact integer cents (`amount_cents = int(round(amount * 100))`).
- **Supported Expressions**:
  - Currency symbols: `$320,000,000.00`, `€45,000`, `£12,500`, `USD 1,200.50`
  - Multipliers: `$320M`, `$96 Million`, `$1.5B`, `$250k`, `500 thousand dollars`
  - Accounting negatives: `($500.00)`, `-$12,450.00`, `($320M)`
  - Edge cases: ignores standalone numbers like years (`2022`), docket numbers (`8:23-cr-00108`), or street addresses (`1456 Cedar Lane`).

### 5.3 Case Docket Normalizer: `normalizers/case_normalizer.py` (Feature 10)
- **Target Invariant**: Extracts and standardizes federal dockets, California Superior Court dockets, police incident numbers, and statutory violation citations.
- **Patterns**:
  - **Federal Dockets**: `(?:8:)?(?:\d{2})-(?:cr|cv|mj|bk|mc)-(?:\d{4,6})(?:-[A-Z0-9\-]+)?`
    - Matches `8:23-cr-00108-CJC`, `8:22-cr-00078-CJC`, `8:23-cr-00009-CJC`, `3:20-mj-05007-TJB`.
  - **California Superior Court**: `30-(?:\d{4})-(?:\d{8})-[A-Z]{2}-[A-Z]{2}-[A-Z0-9]+`
    - Matches `30-2021-01201327-CL-UD-CJC` (Orange County Unlawful Detainer).
  - **Police & Incident Cases**: `Case (?:No\.?\s*)?2019-00053723`, `Case I-2019-001222`, `Summons #2020-613`.
  - **Statutory Citations**: `Cal. Gov. Code § 54220`, `Cal. CCP § 170.6`, `18 U.S.C. § 1343`, `18 U.S.C. § 1951`, `18 U.S.C. § 1961`, `Ralph M. Brown Act`, `Resolution No. 2022-064`.

### 5.4 Correspondence Normalizer: `normalizers/entity_normalizer.py` (Feature 11)
- **Target Invariant**: Parses sender/recipient headers (`FROM:`, `TO:`, `ATTN:`, `MEMORANDUM FOR:`), strips judicial and political honorifics (`Hon.`, `Judge`, `Mayor`, `SA Brian Adkins` $\rightarrow$ `Brian Adkins`), removes email address formatting (`"John Doe" <jdoe@city.gov>` $\rightarrow$ `John Doe`), and computes phonetic blocking keys (Soundex, Double Metaphone).

---

## 6. Memory Management & Invariant Verification Blueprint

### 6.1 Strict Memory Invariants
1. **$O(1)$ Heap Footprint**: Multi-page PDF documents must never accumulate in-memory raster images. Page pixmaps and numpy arrays are deleted immediately inside the generator loop:
   ```python
   del pix
   del img_np
   ```
2. **Periodic Garbage Collection**: Explicit invocation of `gc.collect()` occurs every 10 pages and upon document closure.
3. **RAM Ceiling**: Total process RAM consumption during full extraction workloads is maintained strictly below **250 MB**.

### 6.2 Testing Strategy for Milestone 2

The M2 test suite will be implemented in `workspaces/osintneoai_indexer/tests/test_m2_extraction.py`, providing comprehensive unit, boundary, and scenario validation across 6 major areas:
1. **Unit Tests (Features 5–7)**:
   - PyMuPDF native text extraction and layout preservation.
   - RapidOCR ONNX lazy loading and singleton instance reuse.
   - OpenCV CLAHE contrast enhancement and skew angle calculation.
2. **Boundary & Stress Tests**:
   - 0-byte PDF / corrupted header handling with graceful error recovery.
   - 1-pixel and blank image OCR returning empty string without exceptions.
   - Skewed scan correction ($\pm 35^\circ$ rotated text).
   - Low-contrast / high-noise degraded scans triggering Tier 4 OpenCV fallback.
3. **Multi-Tier Normalizer Validation (Features 8–11)**:
   - ISO 8601 date parsing for US court stamps, military timestamps (`PM 4:29`), and relative dates.
   - Financial amount parsing for `$320M`, `$96 Million`, `($500.00)`, and dual cents verification (`amount_cents == int(round(amount_float * 100))`).
   - Case docket regex validation across federal, California state, and police incident formats.
4. **End-to-End Real World Workloads**:
   - Extraction of Harry Sidhu Plea Agreement (8:23-cr-00108-CJC).
   - Extraction of Todd Ament Information (8:22-cr-00078-CJC).
   - Extraction of HCD Notice of Violation (Cal. Gov. Code § 54220).
   - Memory benchmark testing over a synthetic 100-page scanned PDF verifying memory stays $< 250$ MB.

---

## 7. Implementation Plan for Implementer Agents

| Step | Target File | Action | Key Dependencies |
|---|---|---|---|
| 1 | `workspaces/osintneoai_indexer/extractors/__init__.py` | Module initialization and public exports | None |
| 2 | `workspaces/osintneoai_indexer/extractors/ocr_engine.py` | Implement `OCREngine`, `OCRLine`, `OCRPageResult`, lazy loader, spatial reading order | `rapidocr_onnxruntime`, `pymupdf`, `cv2`, `numpy` |
| 3 | `workspaces/osintneoai_indexer/extractors/image_enhancer.py` | Implement `ImageEnhancer`, CLAHE, adaptive thresholding, deskewing, auto-profile detection | `cv2`, `numpy` |
| 4 | `workspaces/osintneoai_indexer/normalizers/__init__.py` | Module initialization and public exports | None |
| 5 | `workspaces/osintneoai_indexer/normalizers/date_normalizer.py` | Implement ISO 8601 timestamp normalizer | `python-dateutil`, `re`, `datetime` |
| 6 | `workspaces/osintneoai_indexer/normalizers/financial_normalizer.py` | Implement dual float/cents monetary parser | `re` |
| 7 | `workspaces/osintneoai_indexer/normalizers/case_normalizer.py` | Implement federal/state docket & citation parser | `re` |
| 8 | `workspaces/osintneoai_indexer/normalizers/entity_normalizer.py` | Implement correspondence header & honorific cleaner | `re` |
| 9 | `workspaces/osintneoai_indexer/extractors/document_extractor.py` | Implement `DocumentExtractor` 5-Tier Fallback Ladder and `ExtractedRecord` assembler | `pymupdf`, `docx`, `email`, `html.parser`, normalizers |
| 10 | `workspaces/osintneoai_indexer/tests/test_m2_extraction.py` | Implement exhaustive pytest test suite validating Features 5–11 | `pytest`, `tracemalloc` |

---
