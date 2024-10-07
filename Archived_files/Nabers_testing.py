import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

# Load the excel file
file_path = 'Nabers_book.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# Prepare the data
X = df[['Floor (m2)', 'Hours', 'Star Rating']]
y = df['Target Max Electricity kWh per anum']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# List of models to evaluate
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=0.1),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Polynomial Regression': make_pipeline(PolynomialFeatures(2), LinearRegression())
}

# Dictionary to store the R-squared scores of each model
scores = {}

# Evaluate each model
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    scores[name] = score
    print(f"{name} R-squared: {score:.4f}")

# Find the best model
best_model_name = max(scores, key=scores.get)
best_model = models[best_model_name]

print(f"\nBest model: {best_model_name} with R-squared: {scores[best_model_name]:.4f}")

# Train the best model on the full dataset
best_model.fit(X, y)


# Function to calculate Target Max Electricity kWh per anum
def calculate_target_max_electricity(floor_m2, hours, star_rate):
    return best_model.predict(np.array([[floor_m2, hours, star_rate]]))[0]


while True:
    floor_area = int(input("Enter the floor area (m2): "))
    hours = int(input("Enter the hours: "))
    star_rating = int(input("Enter the star rating: "))
    
    target_max_electricity = calculate_target_max_electricity(floor_area, hours, star_rating)
    print(f"The Target Max Electricity kWh per annum for Floor Area: {floor_area} m2, Hours: {hours}, and Star Rating: {star_rating} is {target_max_electricity:.0f} kWh")
    
    choice = input("Do you want to continue? (y/n) ")
    if choice.lower() != 'y':
        break

# Example usage of the function
floor_m2 = floor_area
hours = hours
star_rate = star_rating
target_max_electricity = calculate_target_max_electricity(floor_m2, hours, star_rate)
print(f'Target Max Electricity kWh per anum for {floor_m2} m2 star rating {star_rate} and {hours} hours: {target_max_electricity:.2f}')
