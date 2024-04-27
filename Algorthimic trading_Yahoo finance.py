import yfinance as yf
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Fetch historical data
data = yf.download('AAPL', start='2020-01-01', end='2023-01-01')
data['SMA30'] = data['Close'].rolling(window=30).mean()
data['SMA100'] = data['Close'].rolling(window=100).mean()
# Create a signal for trading
data['Signal'] = 0
data.loc[data['SMA30'] > data['SMA100'], 'Signal'] = 1
data.loc[data['SMA30'] < data['SMA100'], 'Signal'] = -1
# Define the training and test set
train_data = data[data.index < '2022-01-01']
test_data = data[data.index >= '2022-01-01']
# Prepare data for logistic regression
X = train_data[['SMA30', 'SMA100']]
y = train_data['Signal']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Handle any NaNs
X_train.bfill(inplace=True)
X_test.bfill(inplace=True)
test_data[['SMA30', 'SMA100']].bfill(inplace=True)



# Train the model
model = LogisticRegression()
model.fit(X_train, y_train)
# Predict and evaluate the model
y_pred = model.predict(X_test.fillna(method='bfill'))
print(classification_report(y_test, y_pred))
test_data.loc[:, 'Predicted_Signal'] = model.predict(test_data[['SMA30', 'SMA100']].bfill())
# Calculate returns
test_data.loc[:, 'Returns'] = test_data['Close'].pct_change()
test_data.loc[:, 'Strategy_Returns'] = test_data['Returns'] * test_data['Predicted_Signal'].shift(1)

# Plotting the cumulative returns
cumulative_returns = (1 + test_data['Strategy_Returns']).cumprod()
cumulative_returns.plot()
plt.show()  # This ensures that the plot displays correctly
