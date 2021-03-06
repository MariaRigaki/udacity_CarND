import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import time
from sklearn.svm import LinearSVC
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
from utils import *
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, accuracy_score
import pickle
   
    
# Read in cars and notcars
vehicle_dir = './vehicles/'
non_vehicle_dirs = './non-vehicles/'
cars = glob.glob(os.path.join(vehicle_dir, '*/*.png'))
notcars = glob.glob(os.path.join(non_vehicle_dirs, '*/*.png'))

### TODO: Tweak these parameters and see how the results change.
color_space = 'YCrCb' # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
orient = 9  # HOG orientations
pix_per_cell = 8 # HOG pixels per cell
cell_per_block = 2 # HOG cells per block
hog_channel = 'ALL' # Can be 0, 1, 2, or "ALL"
spatial_size = (16, 16) # Spatial binning dimensions
hist_bins = 16    # Number of histogram bins
spatial_feat = True # Spatial features on or off
hist_feat = True # Histogram features on or off
hog_feat = True # HOG features on or off
y_start_stop = [380, 670] # Min and max in y to search in slide_window()

car_features = extract_features(cars, color_space=color_space, 
                        spatial_size=spatial_size, hist_bins=hist_bins, 
                        orient=orient, pix_per_cell=pix_per_cell, 
                        cell_per_block=cell_per_block, 
                        hog_channel=hog_channel, spatial_feat=spatial_feat, 
                        hist_feat=hist_feat, hog_feat=hog_feat)
notcar_features = extract_features(notcars, color_space=color_space, 
                        spatial_size=spatial_size, hist_bins=hist_bins, 
                        orient=orient, pix_per_cell=pix_per_cell, 
                        cell_per_block=cell_per_block, 
                        hog_channel=hog_channel, spatial_feat=spatial_feat, 
                        hist_feat=hist_feat, hog_feat=hog_feat)

X = np.vstack((car_features, notcar_features)).astype(np.float64)                        

# Fit a per-column scaler
X_scaler = StandardScaler().fit(X)

# Apply the scaler to X
scaled_X = X_scaler.transform(X)

pickle.dump(X_scaler, open('scaler.pkl', "wb"))

# Define the labels vector
y = np.hstack((np.ones(len(car_features)), np.zeros(len(notcar_features))))

# Split up data into randomized training and test sets
rand_state = np.random.randint(0, 100)
X_train, X_test, y_train, y_test = train_test_split(
    scaled_X, y, test_size=0.2, random_state=rand_state)

print('Using:',orient,'orientations',pix_per_cell,
    'pixels per cell and', cell_per_block,'cells per block')
print('Feature vector length:', len(X_train[0]))


# Use a linear SVC 
svc = LinearSVC(fit_intercept=False)

# Parameters for grid search
parameters = {'C':[0.001, 0.01, 0.1, 1]}
clf = GridSearchCV(svc, parameters)

# Check the training time for the SVC
t=time.time()

# Train the selector
clf.fit(X_train, y_train)

t2 = time.time()
print(round(t2-t, 2), 'Seconds to train model...')
print("Best estimator: ", clf.best_estimator_)

# Check the score of the SVC
print('Test Accuracy of SVC = ', round(accuracy_score(clf.best_estimator_.predict(X_test), y_test), 4))
print('Confusion matrix: ', confusion_matrix(clf.best_estimator_.predict(X_test), y_test))

pickle.dump(clf.best_estimator_, open('model_svc.pkl', "wb"))

