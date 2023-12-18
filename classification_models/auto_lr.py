# Logistic Regression

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from features_extractors.heterogeneous import Heterogeneous
from sklearn.linear_model import LogisticRegression
from features_extractors.statisticaltime import StatisticalTime



def instantiate_auto_lr():

    lr = Pipeline([
                    ('FeatureExtraction', StatisticalTime()),
                    ('scaler', StandardScaler()),
                    ('lr', LogisticRegression(max_iter=10000)),
                    ])

    #parameters_lr = {'lr__C': [0.1, 0.5, 1]}

    #lr = GridSearchCV(lr, parameters_lr)

    return lr
