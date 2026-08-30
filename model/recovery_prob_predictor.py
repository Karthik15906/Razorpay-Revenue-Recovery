from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (accuracy_score,classification_report,confusion_matrix,roc_auc_score)

import joblib
from xgboost import XGBClassifier
import pandas as pd

df = pd.read_csv('./data/payment_failures.csv')


category = ['payment_method','gateway_status','issuer_status','root_cause']

X = df.drop(columns=["transaction_id","timestamp",'response_code','recovered'])

y = df['recovered']


preprocessor = ColumnTransformer(transformers=[('encoded',OneHotEncoder(sparse_output=False,handle_unknown='ignore'),category)],remainder='passthrough',n_jobs=-1)

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)



model = XGBClassifier(random_state=42,max_depth=3,learning_rate=0.05,n_estimators=150,n_jobs=-1)

pipeline = Pipeline([('preprocessor',preprocessor),('model',model)])

pipeline.fit(X_train,y_train)



y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]



print("Test Accuracy:", accuracy_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nROC-AUC:")
print(roc_auc_score(y_test, y_prob))



# joblib.dump(pipeline,"./model/recovery_probability_pipeline.pkl")

# print("\nRecovery model saved successfully.")

