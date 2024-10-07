import pandas as pd
from functions import NabersPredictor


def main():
    predictor = NabersPredictor()

    # Load data and train/test split
    X_train, X_test, y_train, y_test = predictor.load_data()

    # Evaluate models and find the best one
    predictor.evaluate_models(X_train, X_test, y_train, y_test)

    # Train the best model on the full dataset
    X, y = pd.concat([X_train, X_test]), pd.concat([y_train, y_test])
    predictor.train_best_model(X, y)

    while True:
        # Take inputs from the user
        floor_area = int(input("Enter the floor area (m2): "))
        hours = int(input("Enter the hours: "))
        electricity = float(input("Enter the electricity (kWh): "))

        # Predict the star rating
        predicted_star_rating = predictor.predict_star_rating(floor_area, hours, electricity)
        print(f"The predicted Star Rating is: {predicted_star_rating:.1f}")

        choice = input("Do you want to continue? (y/n) ")
        if choice.lower() != 'y':
            break

if __name__ == '__main__':
    main()

