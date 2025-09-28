"""model.py
Simple ML model wrapper using scikit-learn.
"""
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'reports', 'model.joblib')

class ModelWrapper:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def train(self, X, y):
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)
        self.model.fit(X_train, y_train)
        score = self.model.score(X_val, y_val)
        print(f"Validation accuracy: {score:.4f}")
        return score

    def predict(self, X):
        return self.model.predict(X), self.model.predict_proba(X)

    def save(self, path=MODEL_PATH):
        joblib.dump(self.model, path)

    def load(self, path=MODEL_PATH):
        if os.path.exists(path):
            self.model = joblib.load(path)
            return True
        return False
