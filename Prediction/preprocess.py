df['Gender'] = label_encoder.fit_transform(df['Gender'])
df['Senior Citizen'] = df['Senior Citizen'].map({'No':0,'Yes':1})
df['Partner'].map({'No':1,'Yes':0})
df['Dependents'] = target_encode(df,'Dependents','Churn Value')
df['Phone Service'] = df['Phone Service'].map({'No':0,'Yes':1})
multiple_lines_encoded = pd.get_dummies(df['Multiple Lines'],dtype=int,prefix="phone service")
df = pd.concat([df,multiple_lines_encoded],axis=1)
df.drop('Multiple Lines',axis=1,inplace=True)
df['Internet Service'] = target_encode(df,'Internet Service','Churn Value')
df['Online Security'] = target_encode(df,'Online Security','Churn Value')
df['Online Backup'] = target_encode(df,'Online Backup','Churn Value')
df['Device Protection'] = target_encode(df,'Device Protection','Churn Value')
df['Tech Support'] = target_encode(df,'Tech Support','Churn Value')
df['Streaming TV'] = target_encode(df,'Streaming TV','Churn Value')
df['Streaming Movies'] = target_encode(df,'Streaming Movies','Churn Value')
df['Contract'] = target_encode(df,'Contract','Churn Value')
df['Paperless Billing'] = df['Paperless Billing'].map({'No':0,'Yes':1})
df['Payment Method'] = target_encode(df,'Payment Method','Churn Value')
mask = df['Total Charges'].apply(lambda x: not isinstance(x, (int,float)))
null_rows = df[mask]
not_null_rows = df[~mask]
df.loc[null_rows.index,'Total Charges'] = not_null_rows['Total Charges'].median()
df['Total Charges'] = df['Total Charges'].astype(float)
scale_cols = ['Total Charges', 'Monthly Charges', 'CLTV']
class LogTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, offset=1):
        self.offset = offset

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return np.log(X + self.offset)
pipeline = Pipeline([
    ('log_transform', LogTransformer()),
    ('scaler', RobustScaler())
])
df[scale_cols] = pipeline.fit_transform(df[scale_cols])