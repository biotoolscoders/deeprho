import string
import ctypes
import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.pyplot import MultipleLocator
import scipy.stats
import pandas as pd
import os
import subprocess
import random
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import pearsonr
import time
import multiprocessing as mp
import dendropy
import msprime as msp
from dendropy.calculate.treecompare import unweighted_robinson_foulds_distance
from dendropy.calculate.treecompare import robinson_foulds_distance

def plot(data, color='red', names=None):
    y_major_locator = MultipleLocator(0.3e-7)
    numData = len(data)
    fig, axes = plt.subplots(nrows=numData, figsize=(16,8 * numData), sharey=True)
    if numData == 1:
        axes = [axes]
    for iax in range(numData):
        groundtruth = data[iax][0]
        estimation = data[iax][1]

        axes[iax].yaxis.set_major_locator(y_major_locator)
        axes[iax].plot(groundtruth[0], groundtruth[1], color='black', label='True RecombMap', linewidth=6, alpha=.4)
        axes[iax].plot(estimation[0], estimation[1], color=color, label='Point Estimation', linewidth=2)
        plt.ylim(-0.05e-7, 12e-8)
        axes[iax].set_title(names[iax])
        axes[iax].legend()
    # plt.savefig('{0}.jpg'.format(name), dpi=250)
    plt.show()
    return axes

def summary(results, names=None):
    for data, name in zip(results, names):
        r2 = r2_score(data[0][1][:-1], data[1][1][:-1])
        mae = mean_absolute_error(data[0][1][:-1], data[1][1][:-1])
        mse = mean_squared_error(data[0][1][:-1], data[1][1][:-1])
        pearson = pearsonr(data[0][1][:-1], data[1][1][:-1])
        print('%s R2 SCORE: %.4f, MAE: %f, PEARSON: %.4f' % (name, r2, mae/1e-8, pearson[0]))

def _normalized_ld(data):
    # time1 = time.time()
    rows, cols = data.shape
    freq_vec_1 = np.sum(data, axis=0) / rows
    freq_vec_0 = 1 - freq_vec_1
    freq_vec_1 = freq_vec_1[:, np.newaxis]
    freq_vec_0 = freq_vec_0[:, np.newaxis]
    product = np.dot(data.T, data) / rows
    p1q1 = np.dot(freq_vec_1, freq_vec_1.T)
    p0q0 = np.dot(freq_vec_0, freq_vec_0.T)
    ld = product - p1q1
    ld = ld ** 2 / (p1q1 * p0q0)
    # time2 = time.time()
    # print('time', time2- time1)
    return ld

def _split_windows(data, windowSize=200, skipLength=200):
     popSize, snps = data.shape
     numBins = (snps - windowSize) // skipLength + 1
     windows = []
     print('Totally {0} windows to be predicted.'.format(numBins))
     for i in range(numBins):
         # print('window {0}:'.format(i), [i * skipLength, i * skipLength + windowSize])
         windows.append(data[:, i*skipLength:i*skipLength+windowSize])
     return windows

def _genealogy(data, position=np.array([]), scheme='rentplus'):
    popSize, snps = data.shape
    if scheme == 'rentplus':
        if position.size == 0:
            position = np.arange(1, snps+1) / snps
        rand_name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=4))
        with open('/data/sdd/haotian/temp/{0}.txt'.format(rand_name), 'w') as out:
            for p in position:
                out.write('{:.4f}'.format(p) + ' ')
            out.write('\n')
            for line in data:
                for ele in line:
                    out.write(str(ele))
                out.write('\n')
        _ = subprocess.run('java -jar /home/haz19024/softwares/RentPlus/RentPlus.jar /data/sdd/haotian/temp/{0}.txt'.format(rand_name), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        trees_seq = [tree.strip().split()[1] + ';' for tree in open('/data/sdd/haotian/temp/{0}.txt.trees'.format(rand_name)).readlines()]
    return trees_seq

def _generate_groups(trees_seq):
    tns = dendropy.TaxonNamespace()
    trees = []
    for seq in trees_seq:
        tree = dendropy.Tree.get(data=seq, taxon_namespace=tns, schema='newick')
        trees.append(tree)
    groups = []
    start = 0
    for i, tree in enumerate(trees):
        if tree.as_string(schema='newick') == trees[start].as_string(schema='newick'):
            continue
        else:
            groups.append((start, i))
            start = i
            continue
    groups.append((start, i+1))
    return trees, groups

def _robinson_foulds_parallel(tree1, tree2):
    return unweighted_robinson_foulds_distance(tree1, tree2)

def _robinson_foulds(trees_seq):
    tns = dendropy.TaxonNamespace()
    trees = []
    for seq in trees_seq:
        tree = dendropy.Tree.get(data=seq, taxon_namespace=tns, schema='newick')
        trees.append(tree)
    groups = []
    start = 0
    rf_matrix = np.zeros([len(trees), len(trees)])
    for i, tree in enumerate(trees):
        if tree.as_string(schema='newick') == trees[start].as_string(schema='newick'):
            continue
        else:
            groups.append((start, i))
            start = i
            continue
    print(i)
    groups.append((start, i))
    num_groups = len(groups)
    for g1 in range(num_groups-1):
        for g2 in range(g1, num_groups):
            rf = unweighted_robinson_foulds_distance(trees[groups[g1][0]], trees[groups[g2][0]])
            rf_matrix[groups[g1][0]:groups[g1][1], groups[g2][0]:groups[g2][1]] = rf
            rf_matrix[groups[g2][0]:groups[g2][1], groups[g1][0]:groups[g1][1]] = rf

    return rf_matrix

def _cluster_ld(data):
    da = data.copy()
    i = 0
    rows = data.shape[0]
    while i < rows:
        j = rows
        while j > i:
            temp = data[i:j, i:j]
            if np.sum(temp) / ((j - i) ** 2) > 0.1:  # threshold is 0.1 (can change here)
                da[i:j, i:j] = 1
                i = j - 1
                break
            j = j - 1
        i = i + 1
    return da

def _read_position(file):
    pos = []
    with open(file, 'r') as f:
        for line in f.readlines():
            pos.append(float(line.strip()))
    return np.array(pos)


def _read_fasta(file):
    with open(file, 'r') as f:
        line = f.readline()
        fasta = []
        seq = ''
        while line:
            if line.startswith('>'):
                fasta.append(list(seq))
                seq = ''
                line = f.readline()
                continue
            else:
                seq += line.strip()
                line = f.readline()
        fasta.append(list(seq))
    fasta = fasta[1:]
    for col in range(len(fasta[0])):
        chrs = set()
        for row in range(len(fasta)):
            chrs.add(fasta[row][col])
        sorted_chrs = sorted(chrs)
        assert len(chrs) <= 2, "{0} site should be biallelic.".format(col)
        for row in range(len(fasta)):
            fasta[row][col] = sorted_chrs.index(fasta[row][col])
    return np.array(fasta)

def stat(rates, pos, snpsites, chrLength, Ne4=1e6, skipSize=200, stepSize=200, binWidth=1e5):
    rates = rates.reshape(-1)
    centers = []
    lens = []
    bounds = []
    for i in range(len(rates)):
        # take central point in each interval
        centers.append(pos[int(i*skipSize+ stepSize/2)])
        bounds.append((pos[i*skipSize], pos[min(i*skipSize+stepSize, len(pos)-1)]))
        if i*skipSize + stepSize >= snpsites:
            last = len(rates)-1
        else:
            last = i*skipSize + stepSize
        lens.append(pos[last] - pos[i*skipSize])

    lens = np.array(lens)
    # print('lens' + str(np.max(lens)))
    scaledY = rates / lens / Ne4
    v, bin_edges, _ = scipy.stats.binned_statistic(centers, scaledY, bins=chrLength//binWidth) # range=(0,chrLength)
    return (scaledY, bounds, [bin_edges[:-1], v])

def simulate(output, recombination_rate=1e-8, mutation_rate=1e-8, sample_size=50, length=1e5, Ne=1e4):
    ts = msp.simulate(sample_size=sample_size, mutation_rate=mutation_rate, recombination_rate=recombination_rate, Ne=Ne, length=length)
    with open('results/random1000data/{0}.fas'.format(output), 'w') as out:
        ts.write_fasta(out)
    with open('results/random1000data/{0}.pos'.format(output),'w') as out:
        for site in ts.sites():
            out.write(str(np.round(site.position, 2)))
            out.write(' ')



