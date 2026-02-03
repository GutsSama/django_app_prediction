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


_MODEL = None


def load_model():
    """
    Charge le modèle ML UNE SEULE FOIS
    """
    global _MODEL

    if _MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Le modèle ML est introuvable")

        _MODEL = joblib.load(MODEL_PATH)

    return _MODEL


def predict(data, bmi):
    """
    Fait la prédiction ML
    """
    model = load_model()

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
