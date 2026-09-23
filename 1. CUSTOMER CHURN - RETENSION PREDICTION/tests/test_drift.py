import numpy as np
import pandas as pd
import sklearn
import joblib

from scipy.stats import (
    ks_2samp,
    chi2_contingency
)

from .conftest import (
    NUMERICAL_COLUMNS,
    CATEGORICAL_COLUMNS
)



def numerical_drift(
    reference,
    current,
    column
):

    statistic, p_value = ks_2samp(
        reference[column],
        current[column]
    )

    return {
        "column": column,
        "statistic": statistic,
        "p_value": p_value,
        "drift_detected": p_value < 0.05
    }



def categorical_drift(
    reference,
    current,
    column
):

    reference_counts = (
        reference[column]
        .value_counts()
    )

    current_counts = (
        current[column]
        .value_counts()
    )

    categories = sorted(
        set(reference_counts.index)
        | set(current_counts.index)
    )

    reference_values = [
        reference_counts.get(
            category,
            0
        )
        for category in categories
    ]

    current_values = [
        current_counts.get(
            category,
            0
        )
        for category in categories
    ]

    contingency_table = [
        reference_values,
        current_values
    ]

    chi2, p_value, _, _ = (
        chi2_contingency(
            contingency_table
        )
    )

    return {
        "column": column,
        "chi2": chi2,
        "p_value": p_value,
        "drift_detected": p_value < 0.05
    }



def test_numerical_drift_detector(
    train_df,
    test_df
):

    result = numerical_drift(
        train_df,
        test_df,
        "Age"
    )

    assert "p_value" in result

    assert 0 <= result["p_value"] <= 1



def test_categorical_drift_detector(
    train_df,
    test_df
):

    result = categorical_drift(
        train_df,
        test_df,
        "Gender"
    )

    assert "p_value" in result

    assert 0 <= result["p_value"] <= 1



def test_all_numerical_features(
    train_df,
    test_df
):

    print("\nNUMERICAL DRIFT RESULTS")
    print("-----------------------")

    for column in NUMERICAL_COLUMNS:

        result = numerical_drift(
            train_df,
            test_df,
            column
        )

        print(
            column,
            "p-value =",
            result["p_value"],
            "drift =",
            result["drift_detected"]
        )

        assert 0 <= result["p_value"] <= 1



def test_all_categorical_features(
    train_df,
    test_df
):

    print("\nCATEGORICAL DRIFT RESULTS")
    print("-------------------------")

    for column in CATEGORICAL_COLUMNS:

        result = categorical_drift(
            train_df,
            test_df,
            column
        )

        print(
            column,
            "p-value =",
            result["p_value"],
            "drift =",
            result["drift_detected"]
        )

        assert 0 <= result["p_value"] <= 1



def test_artificial_numerical_drift(
    train_df
):

    reference = train_df[
        "Age"
    ].sample(
        1000,
        random_state=42
    )

    # Artificially shift the distribution.
    shifted = reference + 20

    statistic, p_value = ks_2samp(
        reference,
        shifted
    )

    assert p_value < 0.05