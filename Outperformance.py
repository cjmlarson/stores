import csv
import statistics

import sklearn
from sklearn.feature_selection import RFE
from sklearn.model_selection import cross_val_score, KFold, RepeatedKFold
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

# read in data
data = list(csv.reader(open('adjusted.csv')))
headers = data.pop(0)
num_stores = int(len(data) / 12)

# convert to proper data types
for i in range(len(data)):
    # integer fields
    for j in [0, 1]:
        data[i][j] = int(data[i][j])

    # float fields
    for j in [3, 4, 5, 6, 7]:
        data[i][j] = float(data[i][j])

    # boolean fields
    data[i][8] = (data[i][8] == 'TRUE')

# find monthly averages over year the data
annual = []
for i in range(num_stores):
    to_store = [i + 1, data[12 * i][2], 0, 0, 0, 0, 0]
    for j in range(12):
        for k in [3, 4, 5, 6, 7]:
            to_store[k - 1] += data[12 * i + j][k] / 12
    annual.append(to_store)

# find list of states
states = []
for store in annual:
    if store[1] not in states:
        states.append(store[1])

# set up regressors X and regressand y
# format: [states, revenue, FC/TC, VC/TC, Rent/TC, num. of products]
X = []
y = []

for i in annual:
    y.append((i[2]-sum(i[3:6]))/i[2])
    predictors = [0] * len(states)

    for j in range(len(states)):
        if i[1] == states[j]:
            predictors[j] = 1

    for j in range(3, 6):
        predictors.append(i[j]/sum(i[3:6]))

    predictors.append(i[6])
    X.append(predictors)

# feature selection
lm = LinearRegression()
kf = KFold(5)
min_error = float("-inf")
num_vars = 0

# select i best predictors, train and test model, and store average error
for i in range(len(X[0])):
    # use reverse feature elimination until only i+1 regressors remain
    rfe = RFE(lm, n_features_to_select=i + 1)

    # use k-fold cross-validation to find average error of the model
    pipe = Pipeline(steps=[('s', rfe), ('m', lm)])
    cv = RepeatedKFold()
    scores = cross_val_score(pipe, X, y, scoring='neg_mean_absolute_error', cv=cv)

    # find the number of predictors which minimizes train/test error
    if statistics.mean(scores) > min_error:
        min_error = statistics.mean(scores)
        num_vars = i + 1

# find the coefficients of the model
rfe = RFE(lm, n_features_to_select=num_vars)
rfe.fit(X, y)

# output predictor weights
for i in range(4, 7):
    states.append(headers[i] + "/TC")
states.append("Num. of Products")
used = []

rfe.support_ = list(rfe.support_)
counter = 0
for i in range(len(rfe.support_)):
    if rfe.support_[i]:
        to_append = rfe.estimator_.coef_[counter]
        if abs(to_append) < 1:
            to_append *= 100
        used.append((states[i], to_append))
        counter += 1

# output set of variables and weights
used.insert(0, ("Variable", "Effect (Ratios: per %)"))
csv.writer(open('drivers.csv', mode='w', newline='')).writerows(used)
