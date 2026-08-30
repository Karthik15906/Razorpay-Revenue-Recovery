from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from xgboost import XGBClassifier

import pandas as pd
import joblib as jl


df = pd.read_csv("./data/payment_failures.csv")

category = ['payment_method','gateway_status','issuer_status']

X = df.drop(columns=["root_cause","transaction_id","timestamp",'response_code','recovered'])


y = df["root_cause"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

preprocessor = ColumnTransformer(transformers=[("encoded",OneHotEncoder(sparse_output=False,handle_unknown="ignore"),category)],remainder="passthrough",n_jobs=-1)


le = LabelEncoder()

y_train_encoded = le.fit_transform(y_train)
y_test_encoded = le.transform(y_test)

xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=len(le.classes_),
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", xgb)
    ]
)

pipeline.fit(X_train,y_train_encoded)

y_pred = pipeline.predict(X_test)

y_pred_labels = le.inverse_transform(y_pred)


print(accuracy_score(y_test, y_pred_labels))

print(classification_report(y_test,y_pred_labels))

print(confusion_matrix(y_test,y_pred_labels))


feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()

importance = pd.Series(pipeline.named_steps["model"].feature_importances_,index=feature_names).sort_values(ascending=False)

print(importance)


# artifact = {"pipeline": pipeline,"label_encoder": le}


# jl.dump(
#     artifact,
#     "model/root_cause_model.pkl"
# )

# print("Model saved successfully.")

