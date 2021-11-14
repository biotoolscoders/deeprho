import argparse
import os
import subprocess
import re
from tqdm import tqdm
import multiprocessing as mp
from multiprocessing import Pool
import time 
import threading

parser = argparse.ArgumentParser(description='running rentplus')
parser.add_argument('-d', '--dir', help='directory of files.')
parser.add_argument('-c', '--num-cpu', type=int, help='cpus for use.', default=-1)
args = parser.parse_args()
dirname = args.dir
MAX_CPU_COUNT = mp.cpu_count()
cpu_count = min(args.num_cpu, MAX_CPU_COUNT)

def running_rentplus(file):
    # system calls Rent+
    subprocess.run('java -jar scripts/RentPlus.jar {0}'.format(file), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

if  __name__ == '__main__':
    print('running RentPlus({0} cpu)...'.format(cpu_count ))
    start = time.time()
    files = os.listdir(dirname)
    files = [val for val in files if re.match(r'\d+.txt$', val)]
    with Pool(cpu_count) as pool:
        paths = []
        for file in files:
            abs_path = os.path.join(dirname, file)
            if os.path.isfile(abs_path):
                paths.append(abs_path)
        res = list(tqdm(pool.imap(running_rentplus, paths), total=len(paths), ascii=True, ncols=50))
        pool.close()
        pool.join()

    end = time.time()
        

    print('runtime: {0}'.format(end-start))

    


