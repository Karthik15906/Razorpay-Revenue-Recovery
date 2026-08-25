from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import pandas as pd
import joblib as jl


df = pd.read_csv('./data/cleaned_payment_failures.csv')

response_code_columns = [
    col for col in df.columns
    if col.startswith('encoded__response_code_')
]

X = df.drop(
    columns=[
        'remainder__root_cause',
        'remainder__transaction_id',
        'remainder__timestamp',
        *response_code_columns
    ]
)

y = df['remainder__root_cause']


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


le = LabelEncoder()

y_train_encoded = le.fit_transform(y_train)
y_test_encoded = le.transform(y_test)


xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='multi:softprob',
    num_class=len(le.classes_),
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)


xgb.fit(
    X_train,
    y_train_encoded
)


y_pred = xgb.predict(X_test)

y_pred_labels = le.inverse_transform(y_pred)


print(accuracy_score(y_test, y_pred_labels))

print(
    classification_report(
        y_test,
        y_pred_labels
    )
)

print(
    confusion_matrix(
        y_test,
        y_pred_labels
    )
)


importance = pd.Series(
    xgb.feature_importances_,
    index=X_train.columns
).sort_values(
    ascending=False
)

print(importance)


artifacts = {
    'model': xgb,
    'label_encoder': le
}

jl.dump(
    artifacts,
    'model/root_cause_model.pkl'
)

print("Model saved successfully.")