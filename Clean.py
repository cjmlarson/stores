import csv
import statistics
from sklearn.feature_selection import RFE
from sklearn.model_selection import cross_val_score, KFold, RepeatedKFold
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

# read in data
data = list(csv.reader(open('data.csv')))
headers = data.pop(0)
num_stores = int(len(data)/12)

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

# find monthly averages over year the data, split
owned = []
leased = []

for i in range(num_stores):
    to_store = [i+1, data[12*i][2], 0, 0, 0, 0, 0]
    for j in range(12):
        for k in [3, 4, 5, 6, 7]:
            to_store[k-1] += data[12*i+j][k]/12
    if data[12*i][8]:
        owned.append(to_store)
    else:
        leased.append(to_store)

# find list of states
states = []
for store in leased:
    if store[1] not in states:
        states.append(store[1])

# set up regressors X and regressand y
# format: [states, revenue, fixed, variable, num. of products]
X = []
y = []
for i in leased:
    y.append(i[5])
    predictors = [0] * len(states)

    for j in range(len(states)):
        if i[1] == states[j]:
            predictors[j] = 1

    for j in [2, 3, 4, 6]:
        predictors.append(i[j])

    X.append(predictors)

# feature selection
lm = LinearRegression()
kf = KFold(5)
min_error = float("-inf")
num_vars = 0

# select i best predictors, train and test model, and store average error
for i in range(len(X[0])):
    # use reverse feature elimination until only i+1 regressors remain
    rfe = RFE(lm, n_features_to_select=i+1)

    # use k-fold cross-validation to find average error of the model
    pipe = Pipeline(steps=[('s', rfe), ('m', lm)])
    cv = RepeatedKFold()
    scores = cross_val_score(pipe, X, y, scoring='neg_mean_absolute_error', cv=cv)

    # find the number of predictors which minimizes train/test error
    if statistics.mean(scores) > min_error:
        min_error = statistics.mean(scores)
        num_vars = i+1

# model the rents for the other branches
rfe = RFE(lm, n_features_to_select=num_vars)
rfe.fit(X, y)

# set owned stores in proper format
X_owned = []
for i in owned:
    predictors = [0] * len(states)

    for j in range(len(states)):
        if i[1] == states[j]:
            predictors[j] = 1

    for j in [2, 3, 4, 6]:
        predictors.append(i[j])

    X_owned.append(predictors)

# run predictions using regression model
results = rfe.predict(X_owned)

# output data
owned_nums = [row[0] for row in owned]
data = list(csv.reader(open('data.csv')))
headers = data.pop(0)
headers.append("Profit Margin (Adjusted)")

for row in data:
    if int(row[0]) in owned_nums:
        row[6] = results[owned_nums.index(int(row[0]))]
    row.append((float(row[3]) - float(row[4]) - float(row[5]) - float(row[6]))/float(row[3]))

data.insert(0, headers)
csv.writer(open('adjusted.csv', mode='w', newline='')).writerows(data)
