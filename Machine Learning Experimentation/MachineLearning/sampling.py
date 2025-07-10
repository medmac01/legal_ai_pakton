"""
Description:
Data sampling module that implements oversampling and undersampling techniques using SMOTE for minority class augmentation and random undersampling for class balance adjustment in imbalanced datasets.

Author: Raptopoulos Petros [petrosrapto@gmail.com]
Date : 2025/07/08
"""

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

from collections import Counter

def oversampling_data(X, y):
    """
    Oversamples all minority classes to match the majority class size.
    """
    # sampling_strategy = 1.0 means:
    # "After oversampling, the total of all minority classes = the total of the majority class."
    smote = SMOTE(sampling_strategy='all', random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    print("Class distribution after SMOTE:", Counter(y_res))
    return X_res, y_res

def undersampling_data(X, y):
    """
    Undersample all classes but do not touch the (absolute) minority class(es).
    Each class that is not the minority class will be downsampled to match 
    the minority class' size.
    """
    print("Class distribution before undersampling:", Counter(y))

    # 'not minority' => Undersample every class that has more samples than 
    # the minority class until it matches the minority class size.
    rus = RandomUnderSampler(sampling_strategy='not minority', random_state=42)
    X_res, y_res = rus.fit_resample(X, y)

    print("Class distribution after undersampling:", Counter(y_res))
    return X_res, y_res
