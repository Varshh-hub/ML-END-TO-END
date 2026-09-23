import numpy as np


def test_model_is_pipeline(model):

    assert hasattr(model, "named_steps")

    assert "preprocessor" in model.named_steps

    assert "model" in model.named_steps



def test_preprocessor_exists(model):

    preprocessor = model.named_steps["preprocessor"]

    assert preprocessor is not None



def test_logistic_regression_exists(model):

    classifier = model.named_steps["model"]

    assert classifier is not None

    assert classifier.__class__.__name__ == (
        "LogisticRegression"
    )



def test_preprocessing_transform(
    model,
    X_test
):

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    transformed = preprocessor.transform(
        X_test
    )

    assert transformed.shape[0] == X_test.shape[0]



def test_no_nan_after_preprocessing(
    model,
    X_test
):

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    transformed = preprocessor.transform(
        X_test
    )

    transformed_array = transformed.toarray() \
        if hasattr(transformed, "toarray") \
        else transformed

    assert not np.isnan(
        transformed_array
    ).any()



def test_preprocessing_preserves_rows(
    model,
    X_test
):

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    transformed = preprocessor.transform(
        X_test
    )

    assert transformed.shape[0] == len(X_test)



def test_feature_names_exist(model):

    preprocessor = model.named_steps[
        "preprocessor"
    ]

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    assert len(feature_names) > 0