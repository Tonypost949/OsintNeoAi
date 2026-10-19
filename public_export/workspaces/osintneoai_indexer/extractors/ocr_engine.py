"""
OsintNeoAi Indexer: Neural Offline OCR Engine (RapidOCR ONNX Runtime)
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\extractors\\ocr_engine.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Feature 6

CPU-optimized neural OCR wrapping RapidOCR ONNX with lazy model loading,
spatial reading-order line sorting, confidence filtering, and strict O(1) memory management.
"""

from __future__ import annotations

import gc
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Dict, Generator, Iterable, List, Optional, Sequence, Tuple, Union
import cv2
import numpy as np

logger = logging.getLogger("osintneoai.extractors.ocr_engine")


@dataclass(frozen=True)
class OCRPoint:
    """Represents a 2D coordinate point."""
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
    def top_right(self) -> Tuple[float, float]:
        return self.box[1]

    @property
    def bottom_right(self) -> Tuple[float, float]:
        return self.box[2]

    @property
    def bottom_left(self) -> Tuple[float, float]:
        return self.box[3]

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
    Structured telemetry and transcription container for a single page OCR run.
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


class OCREngine:
    """
    High-accuracy, CPU-optimized Neural OCR engine wrapping RapidOCR ONNX.
    Features lazy model loading, spatial line sorting, confidence filtering,
    and strict memory safety for multi-thousand page archives.
    """

    _instance: Optional[OCREngine] = None

    def __init__(
        self,
        min_confidence: float = 0.30,
        det_use_cuda: bool = False,
        rec_use_cuda: bool = False,
        cls_use_cuda: bool = False,
    ) -> None:
        self.min_confidence = float(min_confidence)
        self.det_use_cuda = det_use_cuda
        self.rec_use_cuda = rec_use_cuda
        self.cls_use_cuda = cls_use_cuda
        self._engine: Optional[Any] = None
        self._is_initialized: bool = False

    @classmethod
    def get_instance(cls, min_confidence: float = 0.30) -> OCREngine:
        """Singleton accessor ensuring loaded ONNX model weights are reused across extractions."""
        if cls._instance is None:
            cls._instance = cls(min_confidence=min_confidence)
        return cls._instance

    def warmup(self) -> None:
        """Explicitly triggers loading of ONNX models into memory."""
        if not self._is_initialized:
            self._get_engine()

    def _get_engine(self) -> Any:
        """Lazy loader for RapidOCR ONNX runtime instance."""
        if self._engine is None:
            logger.info("Initializing RapidOCR ONNX Runtime engine...")
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
            self._is_initialized = True
            logger.info("RapidOCR ONNX Runtime engine initialized.")
        return self._engine

    def ocr_image(
        self,
        image_input: Union[np.ndarray, bytes, str, Path],
        min_confidence: Optional[float] = None,
        page_number: int = 1
    ) -> OCRPageResult:
        """
        Executes OCR on an image array, raw byte payload, or disk file path.
        Returns a structured OCRPageResult with spatial reading-order text.
        """
        engine = self._get_engine()
        min_conf = float(min_confidence) if min_confidence is not None else self.min_confidence

        img_np, should_cleanup = self._prepare_image_array(image_input)

        try:
            h, w = img_np.shape[:2]

            # Execute RapidOCR inference
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
                # RapidOCR format: [box_points, text, confidence]
                raw_box = item[0]
                text = str(item[1]).strip()
                try:
                    conf = float(item[2])
                except (ValueError, TypeError):
                    conf = 0.0

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

    def extract_text_and_confidence(
        self,
        image_input: Union[np.ndarray, bytes, str, Path],
        min_confidence: Optional[float] = None
    ) -> Tuple[List[str], float]:
        """
        Convenience helper returning a tuple of (lines_of_text, avg_confidence).
        """
        res = self.ocr_image(image_input, min_confidence=min_confidence)
        lines = [line.text for line in res.lines]
        return lines, res.avg_confidence

    def _prepare_image_array(
        self,
        image_input: Union[np.ndarray, bytes, str, Path]
    ) -> Tuple[np.ndarray, bool]:
        """Converts heterogeneous image inputs to a normalized 3-channel RGB/BGR uint8 array."""
        if isinstance(image_input, np.ndarray):
            img = image_input
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif len(img.shape) == 3 and img.shape[2] == 4:
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
        Renders pages at specified DPI, processes OCR, destroys pixmaps/numpy arrays,
        and triggers garbage collection every 10 pages.
        """
        import pymupdf

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

                # Periodic GC collection to prevent memory fragmentation
                if (page_idx + 1) % 10 == 0:
                    gc.collect()

                yield result
        finally:
            doc.close()
            gc.collect()


# Alias for cross-module compatibility
RapidOCREngine = OCREngine
