import pandas as pd
import numpy as np
import sklearn
import joblib
import scipy

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    confusion_matrix
)



def calculate_group_metrics(
    y_true,
    y_pred
):

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    false_negative_rate = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate
    }



def compare_groups(
    test_df,
    predictions,
    group_column
):

    results = {}

    for group in test_df[group_column].unique():

        mask = (
            test_df[group_column] == group
        )

        group_y = test_df.loc[
            mask,
            "Churn"
        ]

        group_predictions = predictions[
            mask.to_numpy()
        ]

        # Skip groups without both classes.
        if len(group_y.unique()) < 2:
            continue

        results[group] = calculate_group_metrics(
            group_y,
            group_predictions
        )

    return results



def test_gender_groups_exist(test_df):

    groups = set(
        test_df["Gender"].unique()
    )

    assert "Male" in groups

    assert "Female" in groups



def test_gender_performance(
    model,
    test_df,
    X_test
):

    predictions = model.predict(X_test)

    results = compare_groups(
        test_df,
        predictions,
        "Gender"
    )

    print("\nGENDER FAIRNESS RESULTS")
    print("-----------------------")

    for group, metrics in results.items():

        print(
            group,
            metrics
        )

    assert len(results) >= 2



def test_gender_recall_disparity(
    model,
    test_df,
    X_test
):

    predictions = model.predict(X_test)

    results = compare_groups(
        test_df,
        predictions,
        "Gender"
    )

    recalls = [
        metrics["recall"]
        for metrics in results.values()
    ]

    if len(recalls) >= 2:

        disparity = (
            max(recalls)
            - min(recalls)
        )

        print(
            "\nGender recall disparity:",
            disparity
        )

        # Screening threshold.
        # This is not a universal fairness rule.
        assert disparity < 0.20



def test_subscription_groups(
    model,
    test_df,
    X_test
):

    predictions = model.predict(X_test)

    results = compare_groups(
        test_df,
        predictions,
        "Subscription Type"
    )

    print(
        "\nSUBSCRIPTION TYPE RESULTS"
    )

    for group, metrics in results.items():

        print(group, metrics)

    assert len(results) >= 3



def test_contract_groups(
    model,
    test_df,
    X_test
):

    predictions = model.predict(X_test)

    results = compare_groups(
        test_df,
        predictions,
        "Contract Length"
    )

    print(
        "\nCONTRACT LENGTH RESULTS"
    )

    for group, metrics in results.items():

        print(group, metrics)

    assert len(results) >= 3