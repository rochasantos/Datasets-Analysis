# Balanced Random Forest

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from imblearn.ensemble import BalancedRandomForestClassifier
from features_extractors.statisticaltime import StatisticalTime


def instantiate_balanced_random_forest():
    model = Pipeline([
        ('FeatureExtraction', StatisticalTime()),
        ('scaler', StandardScaler()),
        ('rf', BalancedRandomForestClassifier(sampling_strategy='all', replacement=True)),
    ])
    return model
