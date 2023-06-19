import json

import numpy as np
import pytest
from sklearn.ensemble import IsolationForest

from weaver.unweave import unweave
from weaver.weave import weave


@pytest.mark.parametrize("model", [IsolationForest()])
def test_sklearn_univariate_model(model) -> None:
    data = np.random.rand(500, 10)
    new_example_data = np.random.rand(500, 10)
    model.fit(data)
    res = weave(model)
    roundtrip = unweave(res)
    assert np.all(
        np.equal(
            model.predict(new_example_data),
            roundtrip.predict(new_example_data),
        )
    )
    if hasattr(model, "predict_proba"):
        assert np.all(
            np.equal(
                model.predict_proba(new_example_data),
                roundtrip.predict_proba(new_example_data),
            )
        )
    with open("D:/weaver-json/ExampleSklearnFile.json", "w") as f:
        json.dump(res.as_dict(), f)
    with open("D:/weaver-json/ExampleSklearnMinimalFile.json", "w") as f:
        json.dump(res.as_minimal_dict(), f)
