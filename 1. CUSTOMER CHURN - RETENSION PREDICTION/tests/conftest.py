import pytest
import pandas as pd
import joblib
from pathlib import Path
import numpy as np
import sklearn
import scipy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = PROJECT_ROOT / "churn_train.csv"
TEST_PATH = PROJECT_ROOT / "churn_test.csv"
MODEL_PATH = PROJECT_ROOT / "final_churn_model.pkl"

TARGET_COLUMN = "Churn"

ID_COLUMN = "CustomerID"

NUMERICAL_COLUMNS = [
    "Age",
    "Tenure",
    "Usage Frequency",
    "Support Calls",
    "Payment Delay",
    "Total Spend",
    "Last Interaction"
]

CATEGORICAL_COLUMNS = [
    "Gender",
    "Subscription Type",
    "Contract Length"
]

FEATURE_COLUMNS = NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS

@pytest.fixture(scope="session")
def train_df():

    df = pd.read_csv(TRAIN_PATH)

    # Same cleaning used in your notebook
    df = df.dropna().copy()

    return df

@pytest.fixture(scope="session")
def test_df():

    df = pd.read_csv(TEST_PATH)

    return df.dropna().copy()

@pytest.fixture(scope="session")
def X_test(test_df):

    return test_df.drop(
        columns=[TARGET_COLUMN, ID_COLUMN]
    )


@pytest.fixture(scope="session")
def y_test(test_df):

    return test_df[TARGET_COLUMN]


@pytest.fixture(scope="session")
def model():

    loaded_model = joblib.load(MODEL_PATH)

    return loaded_model

@pytest.fixture(scope="session")
def X_train_data(train_df):

    return train_df.drop(
        columns=[TARGET_COLUMN, ID_COLUMN]
    )


@pytest.fixture(scope="session")
def y_train_data(train_df):

    return train_df[TARGET_COLUMN]