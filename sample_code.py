# -*- coding: utf-8 -*-
"""wheather_sicaklik_mayis_rf_gbr_cnn.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1G4pSeqZetP2hAfjPXsKCRLji_7W4jk2U
"""

!pip install tensorflow_addons
!pip install imutils

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy  as np
import cv2

from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score

from scipy import stats
from scipy.stats import norm


import random


np.random.seed(0)

import warnings
import joblib
# save model

# load model
#gbm_pickle = joblib.load('lgb.pkl')

warnings.filterwarnings('ignore')


import os
from pathlib import Path
import tensorflow
import numpy as np
import scipy.io as sio
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow import keras
from tensorflow.python.ops import math_ops
from tensorflow.python.keras import backend as K


from tensorflow.keras.models import Sequential,   Model
from keras.layers import Dense, LSTM, GRU
from keras.callbacks import ModelCheckpoint
from keras.models import load_model
from keras.layers import LSTM, BatchNormalization, Bidirectional, LayerNormalization
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam, RMSprop
from keras.layers.core import Dense, Activation, Dropout
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import tensorflow as tf
from imutils import paths

import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import matplotlib.style as style
style.use('fivethirtyeight')
import plotly.express as px
import seaborn as sns
sns.set_style('whitegrid')

import os
import warnings
warnings.filterwarnings('ignore')
from joblib import Parallel, delayed

from xgboost import XGBRegressor
import xgboost as xgb

import torch

import lightgbm as lgb
from lightgbm import LGBMRegressor
import pickle

from sklearn.metrics import r2_score
from scipy.stats import norm

import os
import gc
import matplotlib.pyplot as plt

### add random seed
tf.random.set_seed(3)

if not os.path.exists('/data_folder/WHEATHER/performance/'):
   os.makedirs('/data_folder/WHEATHER/performance/')

df = pd.read_excel('/content/istasyonlar_analiz_rasat_5.xlsx')

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.fillna(0, inplace=True)

print(df.columns)

feature_names = [      'Y',	        'X',	       'BAKIDERECE',	    'EGIM',     'YUKSEKLIK',	'DENIZEOLANACI',	'DENIZEOLANUZAKLIK']
#feature_names = [Y-coordinate, X-coordinate,  aspect (degree),      slope,      elevation,      angle to sea,  distance to sea]

#Normalization with max
if 1:
  df['Y'] = df['Y'].values/(df['Y'].values.max())
  df['X'] = df['X'].values/(df['X'].values.max())
  df['BAKIDERECE'] = df['BAKIDERECE'].values/(df['BAKIDERECE'].values.max())
  df['EGIM'] = df['EGIM'].values/(df['EGIM'].values.max())
  df['YUKSEKLIK'] = df['YUKSEKLIK'].values/(df['YUKSEKLIK'].values.max())
  df['DENIZEOLANACI'] = df['DENIZEOLANACI'].values/(df['DENIZEOLANACI'].values.max())
  df['DENIZEOLANUZAKLIK'] = df['DENIZEOLANUZAKLIK'].values/(df['DENIZEOLANUZAKLIK'].values.max())

df.head()

print(df.columns)

df.rename(columns = {'Y':'YC00RDINATE', 'X':'XC00RDINATE',  'BAKIDERECE':'ASPECT(DEGREE)', 'EGIM':'SLOPE', 'YUKSEKLIK':'ALTITUDE', 'DENIZEOLANACI':'DEGREETOSEA', 'DENIZEOLANUZAKLIK':'DISTANCETOSEA'}, inplace = True)

feature_names = ['YC00RDINATE',	'XC00RDINATE',	'ASPECT(DEGREE)',	'SLOPE', 'ALTITUDE',	'DEGREETOSEA',	'DISTANCETOSEA']

df.head()

target = df.SicaklikMayis.values
month_name = 'mayis'
month_id = '05'
wheather_name='sicaklik'

print('num feaures:', len(feature_names))
num_feaures = len(feature_names)
print(feature_names)

X = np.float32( df[feature_names].values )

#X = np.float32( np.array(X) )
y = np.float32(target)
print( X.shape )
print( y.shape )
num_feats =  X.shape[1]
print('num_feats', num_feats)

print(target[0:10])

from sklearn.preprocessing import QuantileTransformer, MinMaxScaler, PowerTransformer, MaxAbsScaler, StandardScaler

#divide dataset into test and train
X_train_indis_name = '/data_folder/WHEATHER/rasat5_inputs_data/x_train_indis.pkl'
X_valid_indis_name = '/data_folder/WHEATHER/rasat5_inputs_data/x_val_indis.pkl'

if 0:

    from sklearn.model_selection import train_test_split

    indices = range(0,len(y))
    x_train, x_val, y_train, y_val, indices_train, indices_test = train_test_split(X, y, indices, test_size=0.20, random_state=41)

    with open(X_train_indis_name, 'wb') as handle:
        pickle.dump(indices_train, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(X_valid_indis_name, 'wb') as handle:
        pickle.dump(indices_test, handle, protocol=pickle.HIGHEST_PROTOCOL)


else:
    indices_train = pickle.load( open(X_train_indis_name,'rb') )
    indices_test = pickle.load( open(X_valid_indis_name,'rb') )

x_train = X[indices_train,:]
x_val = X[indices_test,:]
y_train = y[indices_train]
y_val = y[indices_test]

print(x_train.shape)
print(y_train.shape)
print(x_val.shape)
print(y_val.shape)

num_feats = x_val.shape[1]
print(num_feats)

x_val.shape

x_train.shape

print( y_train[0:10] )
print( y_val[0:10] )

y_train = y_train.reshape(-1, 1)
y_val = y_val.reshape(-1, 1)

if 0:

  from sklearn.preprocessing import QuantileTransformer, MinMaxScaler, PowerTransformer, MaxAbsScaler, StandardScaler

  scaler1 = MinMaxScaler()

  x_train = scaler1.fit_transform(y_train)
  x_val = scaler1.transform(x_val)


  print( y_train[0:10] )
  print( y_val[0:10] )

if 1:
  from sklearn.utils import shuffle
  x_train, y_train = shuffle(x_train, y_train, random_state=0)
  x_val, y_val = shuffle(x_val, y_val, random_state=0)

print( y_train[0:10] )
print( y_val[0:10] )

"""## RF"""

# Function to calculate the root mean squared percentage error
def rmspe(y_true, y_pred):
    #return np.sqrt(np.mean(np.square((y_true - y_pred) / y_true)))
    return (np.mean(np.abs((y_true - y_pred))))

# Function to early stop with root mean squared percentage error
def feval_rmspe(y_pred, lgb_train):
    y_true = lgb_train.get_label()
    return 'RMSPE', rmspe(y_true, y_pred), False

def rmspe3(y_true, y_pred):
    return (K.mean(K.abs((y_true - y_pred) )))
    #return K.sqrt(K.mean(K.square((y_true - y_pred) / y_true)))

from sklearn.ensemble import RandomForestRegressor
def train_and_evaluate_RF(x_train, x_val, y_train, y_val):
    # Hyperparammeters (optimized)
    cv_number = 0

    y_val = np.squeeze(y_val)
    y_train = np.squeeze(y_train)

    model = RandomForestRegressor(max_depth=4,
                                  min_samples_leaf= 16,
                                  min_samples_split= 8,
                                  n_estimators=300,
                                  n_jobs = -1,
                                  criterion="friedman_mse",
                                  random_state=0
                                  )
    model.fit(x_train, y_train)

    model_name= '/data_folder/WHEATHER/performance/cv'+str(cv_number)+'_rf_features'+'.pkl'
    pickle.dump(model, open(model_name, 'wb'))

    # Add predictions to the out of folds array

    y_pred_val = model.predict(x_val)
    y_pred_train =  model.predict(x_train)

    if 1:

      import matplotlib.pyplot as plt
      import seaborn as sns
      import warnings

      warnings.simplefilter(action='ignore', category=FutureWarning)

      # sorted(zip(clf.feature_importances_, X.columns), reverse=Tre)
      feature_imp = pd.DataFrame(sorted(zip(model.feature_importances_, feature_names)), columns=['Value','Feature'])
      feature_imp.sort_values(by="Value", ascending=False)
      feat_imp1 = feature_imp.sort_values(by="Value", ascending=False)
      feat_imp2 = feat_imp1[0:20]


      sns.barplot(x="Value", y="Feature", data=feat_imp2)
      plt.title('Random Forest Regressor Features')
      plt.tight_layout()
      plt.show()

    y_val = np.squeeze(y_val)
    y_train = np.squeeze(y_train)

    print(y_val.shape)
    print(y_pred_val.shape)

    rmspe_score = rmspe(y_val, y_pred_val)
    r2_value = r2_score(y_val, y_pred_val)


    print(f'RMSPE is {rmspe_score}')
    print(f'R2 is {r2_value}')
    # Return test predictions
    return model, y_val, y_pred_val, y_pred_train, y_train

model, y_val, y_pred_val, y_pred_train, y_train = train_and_evaluate_RF(x_train, x_val, y_train, y_val)

y_val[0:10]

y_pred_val[0:10]

import numpy as np
import pandas as pd
df_val = pd.DataFrame({'true':y_val, 'pred':y_pred_val})
df_val.sample(10)

import numpy as np
import pandas as pd
df_train = pd.DataFrame({'true':y_train, 'pred':y_pred_train})
df_train.sample(10)

"""## GBR"""

from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import  GradientBoostingRegressor
from sklearn.inspection import permutation_importance
def train_and_evaluate_GBR(x_train, x_val, y_train, y_val):
    # Hyperparammeters (optimized)
    cv_number = 0

    model=GradientBoostingRegressor()
    model.fit(x_train,y_train)

    model_name= '/data_folder/WHEATHER/performance/cv'+str(cv_number)+'_gbr_features'+'.pkl'
    pickle.dump(model, open(model_name, 'wb'))

    # Add predictions to the out of folds array

    y_pred_val = model.predict(x_val)
    y_pred_train =  model.predict(x_train)

    results = permutation_importance(model, x_val, y_val, scoring='neg_mean_squared_error')
    importance = results.importances_mean
    if 1:

      import matplotlib.pyplot as plt
      import seaborn as sns
      import warnings

      warnings.simplefilter(action='ignore', category=FutureWarning)

      # sorted(zip(clf.feature_importances_, X.columns), reverse=Tre)
      feature_imp = pd.DataFrame(sorted(zip(importance, feature_names)), columns=['Value','Feature'])
      feat_imp1 = feature_imp.sort_values(by="Value", ascending=False)
      feat_imp2 = feat_imp1[0:20]

      sns.barplot(x="Value", y="Feature", data=feat_imp2)
      plt.title('GradientBoostingRegressor Features')
      plt.tight_layout()
      plt.show()


    rmspe_score = rmspe(y_val, y_pred_val)
    r2_value = r2_score(y_val, y_pred_val)
    print(f'RMSPE is {rmspe_score}')
    print(f'R2 is {r2_value}')
    # Return test predictions
    y_val = np.squeeze(y_val)
    y_train = np.squeeze(y_train)
    return model, y_val, y_pred_val, y_pred_train, y_train

model, y_val, y_pred_val, y_pred_train, y_train = train_and_evaluate_GBR(x_train, x_val, y_train, y_val)

import numpy as np
import pandas as pd
df_val = pd.DataFrame({'true':y_val, 'pred':y_pred_val})
df_val.sample(10)

import numpy as np
import pandas as pd
df_train = pd.DataFrame({'true':y_train, 'pred':y_pred_train})
df_train.sample(5)

"""## CNN"""

x_train = np.expand_dims(x_train, 1)
x_val = np.expand_dims(x_val, 1)
y_train = np.expand_dims( y_train,1 )
y_val = np.expand_dims( y_val,1 )


print(y_val.shape)
print(x_train.shape)

def correlation(x, y, axis=-2):
    """Metric returning the Pearson correlation coefficient of two tensors over some axis, default -2."""
    x = tf.convert_to_tensor(x)
    y = math_ops.cast(y, x.dtype)
    n = tf.cast(tf.shape(x)[axis], x.dtype)
    xsum = tf.reduce_sum(x, axis=axis)
    ysum = tf.reduce_sum(y, axis=axis)
    xmean = xsum / n
    ymean = ysum / n
    ###    不偏分散にしたら？？   ###

    xvar = tf.reduce_sum( tf.math.squared_difference(x, xmean), axis=axis)
    yvar = tf.reduce_sum( tf.math.squared_difference(y, ymean), axis=axis)

    cov = tf.reduce_sum( (x - xmean) * (y - ymean), axis=axis)
    corr = cov / tf.sqrt(xvar * yvar)
    return tf.constant(1.0, dtype=x.dtype) - corr

def get_model_gru():



    model = Sequential()
    model.add(layers.GRU(128, return_sequences=True, activation='relu', input_shape=(1, num_feats)))
    model.add(layers.BatchNormalization())

    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Dropout(0.4))

    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.BatchNormalization())
    model.add(layers.Dropout(0.4))

    model.add(layers.Dense(1, activation='linear'))


    rmse = keras.metrics.RootMeanSquaredError(name="rmse")
    #opt = keras.optimizers.Adam(lr=0.001)
    opt = keras.optimizers.RMSprop(lr=0.001)
    #opt = keras.optimizers.SGD(learning_rate=0.001, momentum=0.9)
    model.compile(optimizer=opt, loss='mae', metrics=['mse', "mae", "mape", rmse, correlation])
    return model

model = get_model_gru()
print(model.summary())

x_val.shape

#train the model
cv_number = 0
modelname = 'gru_model_compressor_features'
if 1:
    model_name= '/data_folder/WHEATHER/performance/'+'cv'+str(cv_number)+'_'+modelname+'.hdf5'
    checkpointer = ModelCheckpoint(model_name,period=1, monitor='val_loss', verbose=1, save_best_only=True, mode='min')


    early_stop = EarlyStopping(monitor = 'val_loss', min_delta = 0.0001,
                              patience = 300, mode = 'min', verbose = 1,
                              restore_best_weights = True)

    reduce_lr = ReduceLROnPlateau(monitor = 'val_loss', factor = 0.3,
                                  patience = 70, min_delta = 0.0001,  min_lr=5e-5,
                                  mode = 'min', verbose = 1)

    history = model.fit(x_train, y_train, epochs=1000, batch_size=128, shuffle=True, callbacks=[checkpointer, early_stop, reduce_lr], verbose=1, validation_data=(x_val, y_val) )


    #test the model

if 1:
  plt.figure(figsize=(15,6))
  plt.plot( train_loss )
  plt.plot( val_loss )
  plt.legend(['train','valid'])
  plt.xlabel('Epoch')
  plt.ylabel('Loss')
  plt.show()

model = tf.keras.models.load_model( model_name, custom_objects={"correlation":correlation})

y_pred_val = model.predict(x_val)
y_pred_train = model.predict(x_train)
y_val = np.squeeze(y_val)
y_pred_val = np.squeeze(y_pred_val)
print(y_val.shape)
print(y_pred_val.shape)

r2_value = r2_score(y_val, y_pred_val)
print(f'R2 is {r2_value}')

y_train = np.squeeze(y_train)
y_pred_train = np.squeeze(y_pred_train)
print( y_train.shape )
print( y_pred_train.shape )