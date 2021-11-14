import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
import argparse
import numpy as np
import os 
from utils import stat
import matplotlib.pyplot as plt
parser = argparse.ArgumentParser(description='Prediction of recombination rates.')
parser.add_argument('-i', '--input', help='input of the model.')
parser.add_argument('-p', '--position', help='positions of SNPs.')
parser.add_argument('-m', '--model', help='path of trained model.')
parser.add_argument('-n', '--ne', help='Effective population size.', type=float, default=1e4)
parser.add_argument('-l', '--chrlength', help='length of the whole chromosome.',type=int, default=1)
parser.add_argument('-s', '--scale', help='resolution of prediction on genome.', type=int, default=1e4)
parser.add_argument('-ps', '--popsize', help='population size.', type=int)
parser.add_argument('-sl', '--skiplength', help='length of overlapping.', type=int, default=-1)
args = parser.parse_args()
model_path = args.model
data_path = args.input
dirname = os.path.dirname(data_path)
pos_path = args.position
ne4 = 4 * args.ne
chrlength = args.chrlength
scale = args.scale
popsize = args.popsize
if os.path.exists(data_path):
    x = np.load(data_path)
else:
    print('Data file doesn\'t exist.')
    exit(1)
if os.path.exists(model_path):
    model = keras.models.load_model(model_path)
    # model.summary()
else:
    print('Model file doesn\'t exist.')
    exit(1)
if os.path.exists(pos_path):
    pos = np.load(pos_path)
    pos = pos.reshape(-1)
    # pos = pos * chrlength
else:
    print('Pos file doesn\'t exist.')
    exit(1)

input_shape = model.input.shape[1:]
data_shape = x.shape[1:]

if not input_shape == data_shape:   # check shapes
    print('Input shape doesnt match to model, please check again.')
    exit(1)

def output(rates, bounds, plot_para):
    with open('{dirname}/predict.txt'.format(dirname=dirname), 'w') as out:
        out.write('Rate(cM/Mb)\tStart\tEnd\n')
        for rate, bound in zip(scaled_rates, bounds):
            out.write('{0}\t{1}\t{2}\n'.format(rate, bound[0], bound[1]))
    plt.title('Recombination Rates')
    plt.plot(plot_para[0], plot_para[1], color='red')
    plt.hlines(np.mean(rates), plot_para[0].min(), xmax=plot_para[0].max())
    plt.savefig('{dirname}/map.jpg'.format(dirname=dirname), dpi=200)

windowsize = data_shape[1]
## here test the overlapping cases, where skipsize equals to settings, if skipsize is -1 means we use full windowsize as skipsize. (non-overlapped).
skipsize = args.skiplength
if skipsize == -1:
    skipsize = windowsize

snpsites = pos.shape[-1]
if windowsize == 50:
    x[..., 2] = x[..., 2] / 2 / (popsize-3)
rates = model.predict(x)
scaled_rates, bounds, plot_para = stat(rates, pos, snpsites, chrlength, skipSize=skipsize, stepSize=windowsize, binWidth=scale, Ne4=ne4)
if windowsize == 50:
    scaled_rates = scaled_rates / 97 * (popsize-3)
output(scaled_rates, bounds, plot_para)

avg = 0
total_length = 0
for rate, bound in zip(scaled_rates, bounds):
    avg += rate * (bound[1]-bound[0])
    total_length += (bound[1]-bound[0])
avg = avg / total_length

print('completed!')
print('-------------------  rates -----------------------')
print('weighted average recombination rate %s' % str(avg))
print('--------------------------------------------------')


    

