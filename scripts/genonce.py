###########################################################################
# Program for computing LD, Clustering and Rh of simulated haplotype data.#
#	(NO TREE DISTANCE!)																	  #
#																		  #
###########################################################################
import numpy as np
import pandas as pd
import os
import sys
from tqdm import tqdm

npfile = sys.argv[1]
dirname = os.path.dirname(npfile)

def compute_ld_matrix(data, flag=0):
	# time1 = time.time()
	rows, cols = data.shape
	freq_vec_1 = np.sum(data, axis=0)/rows
	freq_vec_0 = 1 - freq_vec_1
	freq_vec_1 = freq_vec_1[:, np.newaxis]
	freq_vec_0 = freq_vec_0[:, np.newaxis]
	product = np.dot(data.T, data) / rows
	p1q1 = np.dot(freq_vec_1, freq_vec_1.T)
	p0q0 = np.dot(freq_vec_0, freq_vec_0.T)
	ld = product - p1q1
	ld = ld**2 / (p1q1 * p0q0)
	# time2 = time.time()
	# print('time', time2- time1)
	return ld

# currently not used
def getRh(data):
    rows, cols = data.shape
    remain = set()
    Rh = 0
    for i in range(rows):
        if str(data[i, :]) not in remain:
            remain.add(str(data[i, :]))
            Rh += 1
    Rh = Rh - cols
    return Rh

def cluster(data):
    da = data.copy()
    i = 0
    rows = data.shape[0]
    while i < rows:
        j = rows
        while j > i:
            temp = data[i:j, i:j]
            if np.sum(temp) / ((j-i)**2) > 0.1: #threshold is 0.1 (can change here)
                da[i:j, i:j] = 1
                i = j-1
                break
            j = j - 1
        i = i + 1
    return da


msdata = np.load(npfile)
LDs = []
CLs = []
# tqld = tqdm(msdata)
print('calculating LD...')
for i,sample in enumerate(tqdm(msdata, ncols=50, ascii=True)):
#	print('genLD:'+str(i))
	ld = compute_ld_matrix(sample)
	LDs.append(ld)

# tqcl = tqdm(LDs)
print('clustering...')
for i,ld in enumerate(tqdm(LDs, ascii=True, ncols=50)):
#	print('genLDCluster:' +str(i))
	cl = cluster(ld)
	CLs.append(cl)

LDs = np.array(LDs)
CLs = np.array(CLs)
LDs = LDs[..., np.newaxis]
CLs = CLs[..., np.newaxis]
np.save('{dirname}/ld.npy'.format(dirname=dirname), LDs)
np.save('{dirname}/cl.npy'.format(dirname=dirname), CLs)







