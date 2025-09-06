import pandas as pd
import numpy as np
import pytest
from abaloneage.utils.main_utils.utils import load_object

def test_prediction_accuracy():
    # Load test data with actual rings
    df = pd.read_csv('sample_input.csv')
    preprocessor = load_object('final_model/preprocessor.pkl')
    model = load_object('final_model/model.pkl')
    X = df.drop(columns=['rings'])
    X_transformed = preprocessor.transform(X)
    y_pred = model.predict(X_transformed)
    y_true = df['rings'].values
    abs_error = np.abs(y_pred - y_true)
    print("\nPrediction Results:")
    for i, (pred, actual, err) in enumerate(zip(y_pred, y_true, abs_error)):
        status = "OK" if err <= 2 else "FAIL"
        print(f"Row {i}: Predicted={pred:.2f}, Actual={actual}, AbsError={err:.2f} [{status}]")
    mean_abs_error = abs_error.mean()
    print(f"\nMean Absolute Error: {mean_abs_error:.3f}")
    # Allow 80% of predictions within 2 rings
    within_2 = (abs_error <= 2)
    percent_within_2 = within_2.sum() / len(abs_error)
    print(f"{within_2.sum()} out of {len(abs_error)} predictions within 2 rings ({percent_within_2*100:.1f}%)")
    assert percent_within_2 >= 0.8, f"Less than 80% of predictions are within 2 rings. Mean abs error: {mean_abs_error:.3f}"
