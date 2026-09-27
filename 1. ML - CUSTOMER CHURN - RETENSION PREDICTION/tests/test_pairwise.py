import pytest
import pandas as pd
import numpy as np
import sklearn
import joblib
import scipy

def create_customer(
    gender,
    subscription,
    contract
):

    return pd.DataFrame({

        "Age": [35],

        "Tenure": [24],

        "Usage Frequency": [15],

        "Support Calls": [3],

        "Payment Delay": [5],

        "Total Spend": [600],

        "Last Interaction": [10],

        "Gender": [gender],

        "Subscription Type": [
            subscription
        ],

        "Contract Length": [
            contract
        ]
    })



@pytest.mark.parametrize(
    "gender,subscription",
    [
        ("Male", "Basic"),
        ("Male", "Standard"),
        ("Male", "Premium"),
        ("Female", "Basic"),
        ("Female", "Standard"),
        ("Female", "Premium"),
    ]
)
def test_gender_subscription_combinations(
    model,
    gender,
    subscription
):

    customer = create_customer(
        gender=gender,
        subscription=subscription,
        contract="Monthly"
    )

    prediction = model.predict(
        customer
    )

    assert len(prediction) == 1

    assert prediction[0] in [0, 1]



@pytest.mark.parametrize(
    "contract,subscription",
    [
        ("Monthly", "Basic"),
        ("Monthly", "Standard"),
        ("Monthly", "Premium"),

        ("Quarterly", "Basic"),
        ("Quarterly", "Standard"),
        ("Quarterly", "Premium"),

        ("Annual", "Basic"),
        ("Annual", "Standard"),
        ("Annual", "Premium"),
    ]
)
def test_contract_subscription_combinations(
    model,
    contract,
    subscription
):

    customer = create_customer(
        gender="Female",
        subscription=subscription,
        contract=contract
    )

    prediction = model.predict(
        customer
    )

    assert len(prediction) == 1

    assert prediction[0] in [0, 1]



@pytest.mark.parametrize(
    "gender,subscription,contract",
    [
        (
            "Male",
            "Basic",
            "Monthly"
        ),
        (
            "Male",
            "Standard",
            "Annual"
        ),
        (
            "Female",
            "Premium",
            "Quarterly"
        ),
        (
            "Female",
            "Basic",
            "Annual"
        ),
        (
            "Male",
            "Premium",
            "Monthly"
        ),
        (
            "Female",
            "Standard",
            "Quarterly"
        )
    ]
)
def test_customer_combinations(
    model,
    gender,
    subscription,
    contract
):

    customer = create_customer(
        gender=gender,
        subscription=subscription,
        contract=contract
    )

    prediction = model.predict(
        customer
    )

    probability = model.predict_proba(
        customer
    )[0, 1]

    assert prediction[0] in [0, 1]

    assert 0 <= probability <= 1