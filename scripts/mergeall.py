import numpy as np
import sys
import os
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description='merging all npy data.')
parser.add_argument('-d', '--dir', help='directory of files.')
args = parser.parse_args()
dirname = args.dir
ddir = os.path.dirname(dirname)
rf = []
start = 0
def read_java_output(file):
    with open(file) as f:
        line = f.readline()
        size = len(line.strip().split()) + 1
        mat = np.zeros([size, size], np.float16)
        row = 0
        while line:
            values = [float(val) for val in line.strip().split()]
            mat[row, row+1:] = values
            mat[row+1:, row] = values
            line = f.readline()
            row += 1
    return mat

while os.path.exists('{dirname}/{ind}.txt.trees.out'.format(dirname=dirname, ind=str(start))):
    d = read_java_output('{dirname}/{ind}.txt.trees.out'.format(dirname=dirname, ind=str(start)))
    rf.append(d)
    start += 1

# for file in tqdm(os.listdir(dirname)):
#    if 'npy' in file:
#        abs_path = os.path.join(dirname, file)
#        d = np.load(abs_path)
#        rf.append(d)

rf = np.array(rf)[..., np.newaxis]
ld = np.load('{dirname}/ld.npy'.format(dirname=ddir))
cl = np.load('{dirname}/cl.npy'.format(dirname=ddir))


x = np.concatenate([ld, cl, rf], axis=-1)
x = np.array(x, dtype=np.float16)
np.save('{dirname}/x.npy'.format(dirname=ddir), x)

