import os
import joblib
import pandas as pd
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
    if not os.path.exists(MODEL_PATH):
        return None

    return joblib.load(MODEL_PATH)


def predict(data, bmi):
    """
    Fait la prédiction ML
    """
    model = load_model()

    if model is None:
        raise FileNotFoundError("Le modèle ML est introuvable")

    input_data = pd.DataFrame([{
        'age': data['age'],
        'sex': data['sex'],
        'bmi': bmi,
        'children': data['children'],
        'region': data['region'],
        'smoker': data['is_fumeur'],
    }])

    prediction = model.predict(input_data)[0]
    return round(float(prediction), 2)
