import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


class NabersPredictor:

    def __init__(self):
        # Initialize models and scores
        self.models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Polynomial Regression': make_pipeline(PolynomialFeatures(2), LinearRegression())
        }
        self.best_model = None
        self.scores = {}

    def load_all_star_data(self):
        """Load and combine data from all star rating files."""
        # Load data from 4, 5, and 6-star rating files
        files = {
            4: 'data/Nabers_4_Star.xlsx',
            5: 'data/Nabers_5_Star.xlsx',
            #6: 'data/Nabers_6_Star.xlsx'
        }

        combined_data = pd.DataFrame()

        for star, file in files.items():
            df = pd.read_excel(file, sheet_name='Sheet1')
            df['Star Rating'] = star  # Add a column for star rating
            combined_data = pd.concat([combined_data, df])

        return combined_data

    def load_data(self):
        """Load and split the combined star data for training."""
        df = self.load_all_star_data()
        X = df[['Floor (m2)', 'Hours', 'Target Max Electricity kWh per anum']]
        y = df['Star Rating']
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def predict_star_rating(self, floor_m2, hours, electricity):
        """Predict the star rating based on the input values."""
        if self.best_model:
            prediction = self.best_model.predict(np.array([[floor_m2, hours, electricity]]))
            return prediction[0]
        else:
            print("Model not trained yet.")
            return None

    
    def evaluate_models(self, X_train, X_test, y_train, y_test):
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = r2_score(y_test, y_pred)
            self.scores[name] = score
            print(f"{name} R-squared: {score:.4f}")
            
            if name in ['Linear Regression', 'Ridge Regression', 'Lasso Regression']:
                print(f"Model: {name}")
                print(f"Intercept: {model.intercept_}")
                print(f"Coefficients: {model.coef_}")

        # Select the best model based on R-squared score
        self.best_model_name = max(self.scores, key=self.scores.get)
        self.best_model = self.models[self.best_model_name]
        print(f"\nBest model: {self.best_model_name} with R-squared: {self.scores[self.best_model_name]:.4f}")

    def train_best_model(self, X, y):
        self.best_model.fit(X, y)