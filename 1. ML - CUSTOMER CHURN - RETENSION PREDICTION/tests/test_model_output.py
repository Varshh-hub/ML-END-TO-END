import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)



def test_model_can_predict(
    model,
    X_test
):

    predictions = model.predict(X_test)

    assert predictions is not None



def test_prediction_length(
    model,
    X_test
):

    predictions = model.predict(X_test)

    assert len(predictions) == len(X_test)



def test_prediction_values(
    model,
    X_test
):

    predictions = model.predict(X_test)

    unique_predictions = set(
        predictions
    )

    assert unique_predictions.issubset({0, 1})



def test_probability_output(
    model,
    X_test
):

    probabilities = model.predict_proba(
        X_test
    )

    assert probabilities is not None



def test_probability_range(
    model,
    X_test
):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    assert (probabilities >= 0).all()

    assert (probabilities <= 1).all()



def test_probability_length(
    model,
    X_test
):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    assert len(probabilities) == len(X_test)



def test_model_performance(
    model,
    X_test,
    y_test
):

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    print("\nMODEL TEST RESULTS")
    print("------------------")
    print("Accuracy :", accuracy)
    print("Precision:", precision)
    print("Recall   :", recall)
    print("F1 Score :", f1)
    print("ROC-AUC  :", roc_auc)

    # Basic sanity thresholds.
    assert accuracy >= 0.60
    assert roc_auc >= 0.60



def test_predictions_are_finite(
    model,
    X_test
):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    assert np.isfinite(
        probabilities
    ).all()