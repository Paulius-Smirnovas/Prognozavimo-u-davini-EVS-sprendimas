# -*- coding: utf-8 -*-
"""EVS_LD3_Paulius Smirnovas_DIEf21.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HNJyxeyZphC5tCydv-TMfLnREPx52oJX
"""

!pip install kaggle

import os


def get_kaggle_credentials():
  token_dir = os.path.join(os.path.expanduser("~"),".kaggle")
  token_file = os.path.join(token_dir, "kaggle.json")
  if not os.path.isdir(token_dir):
    os.mkdir(token_dir)
  try:
    with open(token_file,'r') as f:
      pass
  except IOError as no_file:
    try:
      from google.colab import files
    except ImportError:
      raise no_file

    uploaded = files.upload()

    if "kaggle.json" not in uploaded:
      raise ValueError("You need an API key! see: "
                       "https://github.com/Kaggle/kaggle-api#api-credentials")
    with open(token_file, "wb") as f:
      f.write(uploaded["kaggle.json"])
    os.chmod(token_file, 600)

get_kaggle_credentials()

! kaggle datasets download -d carrie1/ecommerce-data

# @title Default title text
!unzip ecommerce-data.zip

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import stats


from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import silhouette_samples, silhouette_score

# Set the aesthetic style of the plots
sns.set(style="whitegrid")

from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

data = pd.read_csv("data.csv", encoding="ISO-8859-1")

data.head(10)

data.shape

data["CustomerID"].nunique()

# Summary statistics for numerical variables
data.describe().T

# Summary statistics for categorical variables
data.describe(include='object').T

data["Country"].value_counts(normalize=True)

data.info()

# Convert "InvoiceNo" to a string type series
data["InvoiceNo"] = data.InvoiceNo.astype("str")
# Convert "Description" to a string type series and remove extra whitespaces
data["Description"] = data.Description.astype("str")
data["Description"] = data.Description.str.strip()

data.info()

# Calculate the percentage of null values for each column
null_percentage = data.isnull().mean() * 100
null_percentage

# Removing rows with missing values in 'CustomerID' column
data = data.dropna(subset=["CustomerID"])

# Verifying the removal of missing values
data.isnull().sum().sum()

data.isnull().mean() * 100

data.shape

# Check for duplicate rows
duplicates = data.duplicated()

# Count the number of duplicate rows
duplicates.sum()

data[duplicates]

data = data.drop_duplicates()

data.reset_index(drop=True, inplace=True)

data.head(5)

data.shape

data[
    data["Quantity"] < 0
]

data["is_Cancelled"] = data["InvoiceNo"].apply(lambda x: True if x.startswith('C') else False)
data

data["is_Cancelled"].value_counts(normalize=True)

data[
    data["is_Cancelled"]
].describe().drop('CustomerID', axis=1).T

# Box plot for Quantity
fig_quantity = px.box(data, y="Quantity", notched=True, title="Box Plot of Quantity")
fig_quantity.show()

data[
    ~data["is_Cancelled"]
].describe().drop('CustomerID', axis=1).T

# Box plot for Quantity
fig_quantity = px.box(data[~data["is_Cancelled"]], y="Quantity", notched=True, title="Box Plot of Quantity")
fig_quantity.show()

# Box plot for Quantity
fig_quantity = px.box(data[~data["is_Cancelled"]], y="Quantity", notched=True, title="Box Plot of Quantity", log_y=True)
fig_quantity.show()

data["StockCode"].nunique()

data["len_StockCode"] = data["StockCode"].str.strip().str.len()

data["len_StockCode"].value_counts(normalize=True)

data[
    data["len_StockCode"] == 5
]["StockCode"].nunique()

data[
    data["len_StockCode"] < 5
]

data[
    data["len_StockCode"] < 5
]["StockCode"].value_counts(normalize=True)

data[
    data["len_StockCode"] > 7
]["StockCode"].value_counts(normalize=True)

data[
    (data["len_StockCode"] >= 5) & (data["len_StockCode"] < 8)
]["StockCode"].nunique()

data.shape

data[
    (data["len_StockCode"] >= 5) & (data["len_StockCode"] < 8)
].shape

# Let's calculate the percentage of records with these anomalous stock codes:
percentage_anomalous = ((401604-399689)/401604) * 100
print(f"The percentage of records with anomalous stock codes in the dataset is: {percentage_anomalous:.2f}%")

data = data[
    (data["len_StockCode"] >= 5) & (data["len_StockCode"] < 8)
]

data.shape

# Box plot for UnitPrice
fig_unitprice = px.box(data, y="UnitPrice", notched=True, title="Box Plot of UnitPrice")
fig_unitprice.show()

# Box plot for UnitPrice
fig_unitprice = px.box(
    data,
    y="UnitPrice",
    notched=True,
    title="Box Plot of UnitPrice",
    log_y=True # Set the y-axis to a logarithmic scale
)
fig_unitprice.show()

data["is_Cancelled"].value_counts()

data.shape

data["UnitPrice"].describe()

data[data["UnitPrice"]==0].describe()[["Quantity"]]

data[data["UnitPrice"]==0]

# Removing records with a unit price of zero to avoid potential data entry errors
data = data[data["UnitPrice"] > 0]

def plot_price_quantity_scatter(df):
    """
    Creates a scatter plot to visualize the relationship between unit price and quantity.

    Parameters:
    - df: pandas DataFrame, your dataset containing at least 'Quantity' and 'UnitPrice'.

    Returns:
    - Plotly graph object of the scatter plot.
    """
    # Filter out any potential negative or return quantities and prices
    filtered_df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Create the scatter plot
    fig = px.scatter(filtered_df, x='UnitPrice', y='Quantity', title='Price vs. Quantity',
                     labels={'UnitPrice': 'Unit Price', 'Quantity': 'Quantity'},
                     hover_data=['Description'])  # Assuming 'Description' is a column in the dataframe

    fig.update_layout(xaxis_title='Unit Price', yaxis_title='Quantity',
                      xaxis=dict(type='log'), yaxis=dict(type='log'))  # Log scale for better visualization

    return fig

fig = plot_price_quantity_scatter(data)
fig.show()

data

# Convert InvoiceDate to datetime and set as index
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
viz_data = data.set_index('InvoiceDate')

# Aggregate sales data
viz_data['Sales'] = viz_data['Quantity'] * viz_data['UnitPrice']
daily_sales = viz_data['Sales'].resample('D').sum()  # 'D' for daily

# Time Series Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=daily_sales.index, y=daily_sales, mode='lines', name='Sales'))
fig.update_layout(title='Daily Sales Over Time', xaxis_title='Date', yaxis_title='Sales')
fig.show()

decomposition = seasonal_decompose(daily_sales.dropna(), model='additive')  # Assuming yearly seasonality

# Plot the decomposed components using Plotly
# Note that we use the .observed, .trend, .seasonal, and .resid attributes of the decomposition object
fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                    subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'))

fig.append_trace(go.Scatter(x=daily_sales.index, y=decomposition.observed, mode='lines', name='Observed'), row=1, col=1)
fig.append_trace(go.Scatter(x=daily_sales.index, y=decomposition.trend, mode='lines', name='Trend'), row=2, col=1)
fig.append_trace(go.Scatter(x=daily_sales.index, y=decomposition.seasonal, mode='lines', name='Seasonal'), row=3, col=1)
fig.append_trace(go.Scatter(x=daily_sales.index, y=decomposition.resid, mode='lines', name='Residual'), row=4, col=1)

fig.update_layout(title='Time Series Decomposition')
fig.show()

monthly_sales = viz_data['Sales'].resample('M').sum()

# Plot Monthly Sales
fig = go.Figure([go.Scatter(x=monthly_sales.index, y=monthly_sales)])
fig.update_layout(title='Monthly Sales Over Time', xaxis_title='Month', yaxis_title='Sales')
fig.show()

# Decomposition for Yearly Data might not be as meaningful unless you have multiple years of data
# If you have several years of data and distinct yearly patterns, you can proceed similarly as above

def plot_sales_over_time(df, time_freq='D'):
    """
    Plots the time series of sales volume without the range slider.

    Parameters:
    - df: pandas DataFrame, your dataset containing at least 'InvoiceDate', 'Quantity', and 'UnitPrice'.
    - time_freq: str, the frequency for resampling the time series ('D' for daily, 'W' for weekly, 'M' for monthly, etc.).

    Returns:
    - Plotly graph object of the time series plot.
    """
    # Ensure 'InvoiceDate' is a datetime type
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    # Calculate sales volume
    df['SalesVolume'] = df['Quantity'] * df['UnitPrice']

    # Resample and sum sales volume over the specified time frequency
    sales_over_time = df.resample(time_freq, on='InvoiceDate')['SalesVolume'].sum()

    # Create the time series plot
    fig = px.line(sales_over_time, title='Sales Volume Over Time',
                  labels={'value': 'Sales Volume', 'InvoiceDate': 'Date'},
                  markers=True)  # Adding markers can help visualize individual data points

    # Update the layout to remove the range slider
    fig.update_layout(xaxis_title='Date', yaxis_title='Sales Volume',
                      xaxis=dict(rangeslider=dict(visible=False), type='date'))

    return fig

fig = plot_sales_over_time(data, time_freq='M')  # Monthly sales volume
fig.show()

fig = plot_sales_over_time(data, time_freq='W')  # Weekly sales volume
fig.show()

data

data.to_parquet('your_dataset.parquet')

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import stats


from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import silhouette_samples, silhouette_score

# Set the aesthetic style of the plots
sns.set(style="whitegrid")

from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

df = pd.read_parquet('your_dataset.parquet')

df_sampled = df.sample(frac=0.95, random_state=1)
# Drop these rows from the original DataFrame
df= df.drop(df_sampled.index)

df

df.reset_index(drop=True, inplace=True)

df

pip install numpy pandas scikit-learn matplotlib tensorflow

pip install plotly

df.to_excel(r"data.xlsx", index=True)

data=df
unique_values_Country = df['Country'].unique()
print(unique_values_Country)

unique_values_is_Cancelled = df['is_Cancelled'].unique()
print(unique_values_is_Cancelled)

df.info()

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# Convert InvoiceDate to datetime and set as index
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['DayOfWeek'] = data['InvoiceDate'].dt.dayofweek
data['Hour'] = data['InvoiceDate'].dt.hour

# Define feature set and target variable
data['SalesVolume'] = data['Quantity'] * data['UnitPrice']
X = data[['Quantity', 'UnitPrice', 'StockCode', 'CustomerID', 'Country', 'SalesVolume', 'DayOfWeek', 'Hour']]
y = data['is_Cancelled']

# Define preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['Quantity', 'UnitPrice', 'CustomerID', 'SalesVolume']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Country', 'DayOfWeek', 'Hour', 'StockCode'])
    ])

# Define models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000),
    'Random Forest': RandomForestClassifier(),
    'Neural Network': MLPClassifier(max_iter=300)
}

# Train and evaluate models
results = {}
for name, model in models.items():
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
    pipeline.fit(X, y)
    y_pred = pipeline.predict(X)

    # Evaluation metrics
    accuracy = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    roc_auc = roc_auc_score(y, y_pred)

    results[name] = {
        'Cross-Validation Accuracy': cv_scores.mean(),
        'Accuracy': accuracy,
        'F1 Score': f1,
        'ROC AUC': roc_auc
    }

# Output results
for model_name, metrics in results.items():
    print(f"Model: {model_name}")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    print("\n")


# Hyperparameter tuning for the best model (e.g., Random Forest)
param_grid_rf = {
    'classifier__n_estimators': [100, 200, 300],
    'classifier__max_depth': [None, 10, 20, 30],
    'classifier__min_samples_split': [2, 5, 10]
}

pipeline_rf = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', RandomForestClassifier())])
grid_search_rf = GridSearchCV(pipeline_rf, param_grid_rf, cv=5, scoring='accuracy')
grid_search_rf.fit(X, y)

# Best model evaluation
best_model_rf = grid_search_rf.best_estimator_
y_pred_best = best_model_rf.predict(X)

best_accuracy = accuracy_score(y, y_pred_best)
best_f1 = f1_score(y, y_pred_best)
best_roc_auc = roc_auc_score(y, y_pred_best)

print("Best Model (Random Forest) Performance after Hyperparameter Tuning:")
print(f"Accuracy: {best_accuracy:.4f}")
print(f"F1 Score: {best_f1:.4f}")
print(f"ROC AUC: {best_roc_auc:.4f}")

# Continuing from where we left off in the function
def predict_future(best_model, data, prediction_horizon):
    future_dates = pd.date_range(start=data['InvoiceDate'].max(), periods=prediction_horizon + 1, freq='D')[1:]
    future_data = pd.DataFrame({'InvoiceDate': future_dates})
    future_data['DayOfWeek'] = future_data['InvoiceDate'].dt.dayofweek
    future_data['Hour'] = 0  # Assuming predictions at the start of the day

    # Assuming average values for other features
    future_data['Quantity'] = data['Quantity'].mean()
    future_data['UnitPrice'] = data['UnitPrice'].mean()
    future_data['SalesVolume'] = data['SalesVolume'].mean()
    future_data['StockCode'] = data['StockCode'].mode()[0]
    future_data['CustomerID'] = data['CustomerID'].mean()
    future_data['Country'] = data['Country'].mode()[0]

    X_future = future_data[['Quantity', 'UnitPrice', 'StockCode', 'CustomerID', 'Country', 'SalesVolume', 'DayOfWeek', 'Hour']]

    # Preprocessing the future data
    X_future_preprocessed = best_model.named_steps['preprocessor'].transform(X_future)

    # Making predictions
    y_future_pred = best_model.named_steps['classifier'].predict(X_future_preprocessed)
    future_data['is_Cancelled'] = y_future_pred

    return future_data

# Example usage:
prediction_horizon = 365
future_predictions = predict_future(best_model_rf, data, prediction_horizon)
print(future_predictions)

# Visualizing the predictions
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=future_predictions['InvoiceDate'],
    y=future_predictions['is_Cancelled'],
    mode='lines+markers',
    name='Predicted Cancellations'
))

fig.update_layout(
    title='Predicted Cancellations Over Time',
    xaxis_title='Date',
    yaxis_title='Cancellation Prediction',
    yaxis=dict(tickvals=[0, 1], ticktext=['No', 'Yes'])
)

fig.show()

df.info()
