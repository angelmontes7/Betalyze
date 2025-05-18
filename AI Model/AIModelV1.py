"""
Install
pip install scikit-learn
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score



def modelv1():
    unrevised_matches = pd.read_csv("../data/matches.csv", index_col=0)
    matches = creating_predictors(unrevised_matches)

    rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)

    train = matches[matches["date"] < '2023-01-01'] # train dataset
    test = matches[matches["date"] > '2023-01-01'] # test dataset

    predictors = ["venue_code", "opp_code", "hour", "day_code"]

    rf.fit(train[predictors], train["target"])

    preds = rf.predict(test[predictors])
    acc = accuracy_score(test["target"], preds)

    combined = pd.DataFrame(dict(actual=test["target"], prediction=preds))

    print(pd.crosstab(index=combined["actual"], columns=combined["prediction"]))
    print(precision_score(test["target"], preds))

def creating_predictors(matches):
    matches["date"] = pd.to_datetime(matches["date"]) # switches date from object to datetime
    matches["venue_code"] = matches["venue"].astype("category").cat.codes # converts from string to categories then converting categories to numbers
    matches["opp_code"] = matches["opponent"].astype("category").cat.codes # each team now has there own code/ number
    matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int") # keeps only the hour, removes the colon, and converts to integer
    matches["day_code"] = matches["date"].dt.dayofweek # each day encoded with a number
    matches["target"] = (matches["result"] == "W").astype("int") # If result is W returns true else a false then converts the booleans to 1 or 0

    return matches


def main():
    modelv1()

if __name__ == "__main__":
    main()
