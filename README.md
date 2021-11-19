# DeepRho
DeepRho: software accompanyment for "DeepRho: Accurate Estimation of Recombination Rate from Inferred Genealogies using Deep Learning", Haotian Zhang and Yufeng Wu, manuscript, 2021.

DeepRho constructs images from population genetic data and takes advantage of the power of convolutional neural network (CNN) in image classification to etstimate recombination rate. The key idea of DeepRho is generating genetics-informative images based on inferred gene geneaologies and linkage disequilibrium from population genetic data.

# Code
`deeprho` is an open-source software developed for per-base recombination rate estimation from inferred genealogies using deep learning. `deeprho` makes estimates based on LD patterns and local genealogical trees inferred by *RENT+*[^1].

---
### Requirements
- Runtime: Linux with Python3 and Java Runtime Environment(or JDK).
- numpy >= 1.19.0
- pandas >= 1.2.5
- matplotlib >= 3.4.2
- tensorflow >= 2.4.0 (GPU version is preferred)
- tqdm >= 4.61.1

Note: `java` should be added to `$PATH` and is able to be executed anywhere in system.

### Input formats
- MS-like format
- Fasta (coming soon)

### Usage
1. Unzip `deeprho` into any directory, for example `/path/to/deeprho`.
2. Enter that directory `cd /path/to/deeprho`
3. Run `./deeprho -f data/ms.data -w 50 -s 100 -m pretrain_models/snp50_rho200.mdl -n 100000 -l 100000 -r 1000`
4. | Arguments |       Alternative Names        |  Descriptions                                                |
   | --------- | ------------------------------ | -------------------------------------------------------------|
   | -f        | --msfile <MSFILE>              | Path of MS-format input                                      |
   | -w        | --window-size <WINDOWSIZE>     | Size for each slidding window (only 50 can be used currently)|
   | -s        | --sample-size <POPSIZE>        | Samples size                                                 |
   | -m        | --model <MODEL>                | Path of trained model                                        |
   | -n        | --effective-popsize            | Effective population size                                    |
   | -l        | --chr-length                   | Length of haplotypes in unit bp                              |
   | -r        | --resolution                   | Resoulution of recombination rates(ex. 1000 means rates/1kbp)|
   | -h        | --help                         | Show usage                                                   |
5. File `data/predict.txt` shows the inferred recombination map.
6. Type `./deeprho --help` to review usage.
  
Notes: `deeprho` should be ran directly under its root directory. As `deeprho` will generate a bunch of intermediate files inside the folder where inputs are, to avoid confliction, we strongly suggest users to create a new folder for each input file respectively.

### Results
`data/map.jpg` plots the recombination map.

Contact Email: haotianzh@uconn.edu.
    
### Reference:
[^1]: Mirzaei S, Wu Y. RENT+: an improved method for inferring local genealogical trees from haplotypes with recombination. Bioinformatics. 2017 Apr 1;33(7):1021-1030.
  
