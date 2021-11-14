import os
import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='This is a program used to read data from ms software and convert it to some other format.')
parser.add_argument('-f', '--file',  help='input filename.', type=str)
parser.add_argument('-c','--convert', help='convert to other format.', type=str)
parser.add_argument('-s', '--save', default=False, action='store_true', help='save numpy matrix of msdata')
parser.add_argument('-l', '--length', help='chromosome length, provided if there are not physical positions.', type=int, default=1)
args = parser.parse_args()
filename = args.file
dirname = os.path.dirname(filename)
convert = args.convert
length = args.length
f = open(filename, 'r')
ms_command = f.readline().strip().split()
pop_size = int(ms_command[1])
sample_size = int(ms_command[2])
random_seeds = f.readline().strip().split()
data = {'ms_command': ms_command, 'ms_data': [], 'ms_str': []}
# read for ms outputs
labels = []
sample_data = [] # initial list for each sample.
sample_str = ''
line = 'a'
count = 0
# print(args)
while line:
    line = f.readline()
    if line.strip() == '':
        count += 1
        if line:
            # print("sample id: ", count)
            pass
        if sample_str:
            data['ms_str'].append(sample_str)
        if args.save and sample_data:
            data['ms_data'].append(np.array(sample_data))  # append a new sample into memory
        sample_data = []
        sample_str = ''
        continue
    if line.startswith('//'):
        if len(line.strip().split()) == 1:
            pass
        else:
            label = float(line.strip().split()[1])
            labels.append(label)
        continue
    if not line[0].isdigit():
        key, values = line.strip().split(':')
        if key in data:
            data[key].append(np.array([float(val) for val in values.strip().split()]))
        else:
            data[key] = [np.array([float(val) for val in values.strip().split()])]
        continue
    else:
        sample_str += line
        if args.save:
            sample_data.append([int(val) for val in list(line.strip())])
        continue

for i, positions in enumerate(data['positions']):
    data['positions'][i] =  np.array(positions) * length
    data['positions'][i] = data['positions'][i].astype(int)
    if data['positions'][i][0] == 0:
        data['positions'][i][0] = 1
    

data['labels'] = labels

# print("total samples # :", count -1)

if not count-1 == sample_size:
    print('counts is not equal to sample size, double check it.')

# os.chdir(os.path.dirname(filename))
if convert:
    if not os.path.exists('{dirname}/_data'.format(dirname=dirname)):
        os.mkdir('{dirname}/_data'.format(dirname=dirname))
    pars = convert.split()
    for i in range(count-1):
        # print('file %d' % i)
        out = open('{dirname}/_data/{ind}.txt'.format(dirname=dirname, ind=i) , 'w')
        for par in pars:
            if par == 'ms_str':
                out.write(data[par][i])
                out.write('\n')
            else:
                out.write(' '.join([str(val) for val in data[par][i]]))
                out.write('\n')
        out.flush()
        out.close()

if args.save:
    np.save('{dirname}/ms.values'.format(dirname=dirname), data['ms_data'])
    np.save('{dirname}/ms.labels'.format(dirname=dirname), np.array(data['labels']))
    np.save('{dirname}/ms.pos'.format(dirname=dirname), np.array(data['positions']))
