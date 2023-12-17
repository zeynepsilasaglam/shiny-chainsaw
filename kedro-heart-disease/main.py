from fastapi import FastAPI, Query, Body, Depends
from typing_extensions import Annotated# typing_ext for python <= 3.9 
from typing import List, Any
from pydantic import BaseModel
from enum import Enum
import pandas as pd
from src.kedro_heart_disease.nodes import train, predict, check_model, model_score
import src.kedro_heart_disease.nodes
import numpy as np

app = FastAPI()

#returns list of models 
@app.get("/models")
def greet() -> List[str]: 
    return [model.value for model in Models]


class Output(BaseModel):
    target: int

#takes model name and row. Request body sample: [62, 0, 0, 124, 209, 0, 1, 163, 0, 0, 2, 0, 2]

class Models(str, Enum):
    rand_for = "RandomForestClassifier",
    knn = "KNeighborsClassifier",
    gauss = "GaussianNB"


@app.post("/predict")
def predict_(model_name: Annotated[Models, Query()],
    input: Annotated[List[int], Body()]) -> str:
    src.kedro_heart_disease.nodes.current_model = check_model(model_name.value)

    inp = pd.DataFrame([input])
    result = predict(src.kedro_heart_disease.nodes.current_model, inp)
    format_result = np.array2string(result, separator=' ')[1:-1]
    return f"Predicted: {format_result}"

'''
{
  "input": [
    62, 0, 0, 124, 209, 0, 1, 163, 0, 0, 2, 0, 2
  ],
  "expected_output": {
    "target": 1
  }
}
'''

@app.post("/train")
def train_(model_name: Annotated[Models, Query()],
    input: Annotated[List[int], Body()],
    expected_output: Annotated[Output, Body()]) -> str:

    src.kedro_heart_disease.nodes.current_model = check_model(model_name.value)
    df = pd.DataFrame([input])
    eo = pd.DataFrame({"target": [expected_output.target]})
    train(src.kedro_heart_disease.nodes.current_model, df, eo)

    return model_score(src.kedro_heart_disease.nodes.current_model)


