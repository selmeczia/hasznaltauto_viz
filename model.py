from typing import Any
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import plotly.express as px
import webbrowser
from plotly.offline import plot
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

import re



class CarPriceModel():
    FEATURE_COLS = ["age_in_months", "motor_size", "motor_kw", "motor_hp", "mileage_km"]
    TARGET_COL = "price"

    def __init__(self, raw_df) -> None:
        self.raw_df = raw_df
        pass

    def __call__(self) -> pd.DataFrame:

        preprocessed_df = self.preprocess_df(self.raw_df)
        predicted_df = self.create_model(preprocessed_df)
        processed_df = self.process_df(predicted_df)

        return processed_df


    def create_model(self, df_raw):

        df = df_raw.copy()

        # Split df into features and target
        features = df[self.FEATURE_COLS].copy()
        target = df[self.TARGET_COL].copy()

        # Create the model
        model = LinearRegression()

        # Perform K-fold cross-validation
        k = 5  # Number of folds
        kf = KFold(n_splits=k, shuffle=True, random_state=42)

        # Initialize an array to store the predicted prices
        all_predictions = []

        for train_index, test_index in kf.split(features):
            # Split the data into training and testing sets for the current fold
            X_train, X_test = features.iloc[train_index], features.iloc[test_index]
            y_train, y_test = target.iloc[train_index], target.iloc[test_index]

            # Fit the model on the training set
            model.fit(X_train, y_train)

            # Make predictions on the testing set
            fold_predictions = model.predict(X_test)

            # Append the predictions to the array
            all_predictions.extend(fold_predictions)

        # Calculate RMSE on the entire dataset
        rmse = mean_squared_error(target, all_predictions, squared=False)
        print("RMSE:", rmse)

        # Fit the final model on the entire dataset
        model.fit(features, target)
        final_predictions = model.predict(features)

        # Assign the final predictions to the DataFrame
        df["predicted_price"] = final_predictions

        return df
    
    def preprocess_df(self, df) -> pd.DataFrame:
        return df.dropna(axis=0)

    def process_df(self, df_raw) -> pd.DataFrame:

        # df['gas_type'] = np.where(df['gas_type_Benzin'] == 1, 'Benzin', 'Dízel')
        # df['comfort'] = np.where(df['comfort_trendline'] == 1,
        #                         'trendline',
        #                         np.where(df["comfort_highline"],
        #                                 "highline",
        #                                 np.where(df["comfort_comfortline"] == 1, "comfortline", None)))

        # df['gas_type_code'] = df['gas_type'].astype('category').cat.codes

        df = df_raw.copy()
        df['age'] = (df["age_in_months"] / 12)

        return df


    def create_dummy_variables(self, df: pd.DataFrame, variables: list):
        # Add dummy variables
        df = pd.get_dummies(self.df, columns=['comfort', 'gas_type'])
        df = df.dropna(axis=0)




