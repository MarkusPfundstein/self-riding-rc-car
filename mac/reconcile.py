import pandas as pd
import numpy as np

readings = pd.read_csv('readings.csv')
frames = pd.read_csv('frames.csv')

merged = pd.merge_asof(left=readings, right=frames, left_on='ts', right_on='ts')

def get_forward_control(c):
    return int(c & (1 << 0) != 0)

def get_backward_control(c):
    return int(c & (1 << 1) != 0)

def get_left_control(c):
    return int(c & (1 << 2) != 0)

def get_right_control(c):
    return int(c & (1 << 3) != 0)

merged['forward'] = np.vectorize(get_forward_control)(merged['controls'])
merged['backward'] = np.vectorize(get_backward_control)(merged['controls'])
merged['left'] = np.vectorize(get_left_control)(merged['controls'])
merged['right'] = np.vectorize(get_right_control)(merged['controls'])

print(merged)

merged.to_csv('merged.csv')
