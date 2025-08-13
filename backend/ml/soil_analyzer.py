import base64
import io
import os
from pathlib import Path
from typing import Dict, Any

import numpy as np
import cv2


_MODELS_DIR = Path('Machine Learning/Deployed models testing')


def _load_models():
    import pickle
    models = {}
    try:
        with open(_MODELS_DIR / 'Pclassifier.pkl', 'rb') as f:
            models['P'] = pickle.load(f)
    except Exception:
        models['P'] = None
    try:
        with open(_MODELS_DIR / 'pHclassifier.pkl', 'rb') as f:
            models['pH'] = pickle.load(f)
    except Exception:
        models['pH'] = None
    try:
        with open(_MODELS_DIR / 'OMclassifier.pkl', 'rb') as f:
            models['OM'] = pickle.load(f)
    except Exception:
        models['OM'] = None
    try:
        with open(_MODELS_DIR / 'ECclassifier.pkl', 'rb') as f:
            models['EC'] = pickle.load(f)
    except Exception:
        models['EC'] = None
    return models


_CACHED_MODELS = None


def _get_models():
    global _CACHED_MODELS
    if _CACHED_MODELS is None:
        _CACHED_MODELS = _load_models()
    return _CACHED_MODELS


def _extract_temp_feature(image_bgr: np.ndarray) -> float:
    blue_channel = image_bgr[:, :, 0]
    green_channel = image_bgr[:, :, 1]
    red_channel = image_bgr[:, :, 2]
    value = (np.median(green_channel) + np.median(blue_channel)) + np.median(red_channel)
    return float(np.nanmean(value))


def analyze_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('Invalid image data')

    feature = _extract_temp_feature(image)

    models = _get_models()
    results = {}
    for key in ['P', 'pH', 'OM', 'EC']:
        model = models.get(key)
        try:
            if model is not None:
                pred = float(model.predict([[feature]]))
            else:
                pred = float(feature % 10)
        except Exception:
            pred = float(feature % 10)
        results[key] = round(pred, 3)

    # Add a naive moisture proxy from intensity spread
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    moisture_proxy = float(1.0 - (np.std(gray) / 128.0))
    moisture_proxy = max(0.0, min(1.0, moisture_proxy))
    results['moisture'] = round(moisture_proxy, 3)

    return results


