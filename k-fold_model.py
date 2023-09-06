import pandas as pd
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd
from sklearn.metrics import mean_squared_error
from plotly.offline import plot
import plotly.graph_objs as go
import re
import numpy as np
from sklearn.feature_selection import RFE

# Load the car ads DataFrame
car_ads_df = pd.read_csv('scraped_data/volkswagen_golf_6_1.4_benzin.csv')

# Select features and target variable
df = car_ads_df
df = pd.get_dummies(df, columns=['comfort', 'gas_type'])
df = df.dropna(axis=0)
features = df[['age_in_months', 'motor_size', 'motor_kw', 'motor_hp', 'mileage_km',
                'comfort_comfortline', 'comfort_highline', 'comfort_trendline', 'gas_type_Benzin',
                # 'gas_type_Dízel'
                ]]
target = df['price']

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
predictions = model.predict(features)

df["predicted_price"] = predictions
df['gas_type'] = np.where(df['gas_type_Benzin'] == 1, 'Benzin', 'Dízel')
df['comfort'] = np.where(df['comfort_trendline'] == 1,
                         'trendline',
                         np.where(df["comfort_highline"],
                                  "highline",
                                  np.where(df["comfort_comfortline"] == 1, "comfortline", None)))

df['gas_type_code'] = df['gas_type'].astype('category').cat.codes
df['age'] = df["age_in_months"] / 12

# PLOT

filtered_df = df.loc[(df["gas_type"] == "Benzin") & (df["motor_size"] > 1350) & (df["motor_size"] < 1450)]

def set_shape(x):
    if(x == "trendline"):
        return "green"
    elif(x == "comfortline"):
        return "yellow"
    elif(x == "highline"):
        return "red"
    else:
        return "lightblue"


def create_plot(df, title, file_name):

    data = [
        go.Scatter(
            x=df["price"],
            y=df['predicted_price'],
            mode='markers',
            name='',
            text=df["title"],
            customdata=df["link"],
            marker=dict(
                color=df["age"],
                showscale=True,
                size=df["mileage_km"],
                sizeref=2.*max(df["mileage_km"])/(50.**1),
                sizemin=4,
                # line=dict(width=5, color=list(map(set_shape, df["comfort"])))
            ),
            hovertemplate =
                'Title: %{text}<br>'+
                'Predicted price: %{y:.3s} Ft <br>'+
                'Actual price: %{x:.3s} Ft <br>' + 
                'Age: %{marker.color:.1f} years <br>' +
                'Mileage: %{marker.size:,.0f} km'
        )
    ]

    line_trace = go.Scatter(
        x=[min(df["price"]), max(df["price"])],
        y=[min(df["price"]), max(df["price"])],
        mode='lines',
        name='x=y'
    )

    data.append(line_trace)

    # Build layout
    layout = go.Layout(
        hovermode='closest',
        showlegend=False,
        xaxis=dict(title="Price", tickfont=dict(size=14)),
        yaxis=dict(title="Predicted Price", tickfont=dict(size=14)),
        title=f"{title.capitalize()} {file_name.replace('_', ' ')} Price Prediction",
        font=dict(size=16)
    )

    # Build Figure
    fig = go.Figure(
        data=data,
        layout=layout,
    )

    # Get HTML representation of plotly.js and this figure
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Get id of html div element that looks like
    # <div id="301d22ab-bfba-4621-8f5d-dc4fd855bb33" ... >
    res = re.search('<div id="([^"]*)"', plot_div)
    div_id = res.groups()[0]

    # Build JavaScript callback for handling clicks
    # and opening the URL in the trace's customdata 
    js_callback = """
    <script>
    var plot_element = document.getElementById("{div_id}");
    plot_element.on('plotly_click', function(data){{
        console.log(data);
        var point = data.points[0];
        if (point) {{
            console.log(point.customdata);
            window.open(point.customdata);
        }}
    }})
    </script>
    """.format(div_id=div_id)

    # Build HTML string
    html_str = """
    <html>
    <body>
    {plot_div}
    {js_callback}
    </body>
    </html>
    """.format(plot_div=plot_div, js_callback=js_callback)

    # Write out HTML file
    with open(f'{file_name}.html', 'w') as f:
        f.write(html_str)


create_plot(filtered_df, "Volkswagen Golf 6", "vw_golf_6")