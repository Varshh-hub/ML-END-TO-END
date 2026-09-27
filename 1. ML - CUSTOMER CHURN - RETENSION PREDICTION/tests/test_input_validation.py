import pandas as pd
import numpy as np
import sklearn
import joblib
import scipy

from .conftest import (
    FEATURE_COLUMNS,
    NUMERICAL_COLUMNS,
    CATEGORICAL_COLUMNS,
    TARGET_COLUMN,
    ID_COLUMN
)



def test_required_columns_exist(test_df):

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN, ID_COLUMN]
    )

    for column in required_columns:

        assert column in test_df.columns, (
            f"Missing required column: {column}"
        )



def test_column_structure(test_df):

    expected_columns = set(
        FEATURE_COLUMNS
        + [TARGET_COLUMN, ID_COLUMN]
    )

    actual_columns = set(test_df.columns)

    assert actual_columns == expected_columns



def test_no_missing_values(test_df):

    assert test_df.isnull().sum().sum() == 0



def test_no_duplicate_rows(test_df):

    assert test_df.duplicated().sum() == 0



def test_numerical_columns_are_numeric(test_df):

    for column in NUMERICAL_COLUMNS:

        assert pd.api.types.is_numeric_dtype(
            test_df[column]
        ), f"{column} should be numeric"



def test_categorical_columns(test_df):

    for column in CATEGORICAL_COLUMNS:

        assert test_df[column].dtype == "object", (
            f"{column} should contain categorical values"
        )



def test_churn_is_binary(test_df):

    unique_values = set(
        test_df[TARGET_COLUMN].unique()
    )

    assert unique_values.issubset({0, 1}), (
        "Churn must contain only 0 and 1"
    )



def test_numerical_ranges(test_df):

    for column in NUMERICAL_COLUMNS:

        assert (test_df[column] >= 0).all(), (
            f"{column} contains negative values"
        )



def test_age_range(test_df):

    assert test_df["Age"].between(18, 65).all()



def test_categorical_values(test_df):

    expected_values = {
        "Gender": {"Male", "Female"},

        "Subscription Type": {
            "Basic",
            "Standard",
            "Premium"
        },

        "Contract Length": {
            "Monthly",
            "Quarterly",
            "Annual"
        }
    }

    for column, allowed_values in expected_values.items():

        actual_values = set(
            test_df[column].unique()
        )

        assert actual_values.issubset(
            allowed_values
        ), f"Unexpected value found in {column}"