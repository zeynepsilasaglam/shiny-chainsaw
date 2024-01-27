"""
This is a boilerplate pipeline
generated using Kedro 0.18.14
"""

from importlib.machinery import ModuleSpec
import logging
from typing import Any, Dict
from kedro_datasets.pickle import PickleDataSet
from kedro_datasets.pandas import CSVDataset
from kedro.io import DataCatalog
io = DataCatalog(datasets={
                  "heart_disease_data": CSVDataset(filepath="data/01_raw/heart.csv")
                  })

import pandas as pd
from sklearn.metrics import f1_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import log_loss
from enum import Enum

import logging

class ModelNames(Enum):
    GAUSSIAN_NB = "GaussianNB"
    RANDOM_FOREST = "RandomForestClassifier"
    LR_MODEL = "LogisticRegression"

rf_model = PickleDataSet(filepath="data/06_models/rf_model.pkl").load()
gnb_model = PickleDataSet(filepath="data/06_models/gnb_model.pkl").load()
lr_model = PickleDataSet(filepath="data/06_models/lr_model.pkl").load()
current_model = rf_model

def check_model(model_name: str):
    try:
        return {
            ModelNames.RANDOM_FOREST: rf_model,
            ModelNames.LR_MODEL: lr_model,
            ModelNames.GAUSSIAN_NB: gnb_model,
        }[ModelNames(model_name)]
    except ValueError:
        raise ValueError("Unknown algorithm name")     
            

def get_model(model: str):
    current_model = check_model(model)
    return current_model

def get_current_model():
    return current_model 

def split_data(data: pd.DataFrame):
    data_train = data.sample(frac=0.7, random_state=42)
    data_test = data.drop(data_train.index)
    X_train = data_train.drop(columns="target")
    X_test = data_test.drop(columns="target")
    y_train = data_train["target"]
    y_test = data_test["target"]
    return X_train, X_test, y_train, y_test

def model_score(model):
    data = io.load("heart_disease_data")
    logging.warning('data was loaded')
    X_train, X_test, y_train, y_test = split_data(data)
    y_train = y_train.values
    print(X_test.values)
    print(X_test.values.shape)
    logging.warning(' i am about to predict')
    columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    X_test.columns = columns
    y_pred = model.predict(X_test)
    print(X_test)
    score = ''
    if type(model).__name__ == ModelNames.RANDOM_FOREST.value:
        score = f1_score(y_test, y_pred, average='weighted')
    if type(model).__name__ == ModelNames.GAUSSIAN_NB.value:
        score = mean_squared_error(y_test, y_pred)
    if type(model).__name__ == ModelNames.LR_MODEL.value:
        score = log_loss(y_test, y_pred)
    return score


def train(model, X_train: pd.DataFrame, y_train: pd.DataFrame):
    columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    X_train.columns = columns
    y_train.columns = ["target"]
    current_model = model.fit(X_train, y_train)
    

def predict(model, data: pd.DataFrame) :
    columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    data.columns = columns
    prediction = model.predict(data)
    return prediction
