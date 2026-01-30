import joblib
import os
from django.conf import settings


MODEL_PATH = os.path.join(
    settings.BASE_DIR, 
    'apps', 
    'prediction', 
    'ml_models', 
    'insurance_model.joblib'
)


def load_model():
    """
    Charge et retourne le modèle ML.
    """
    
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None