# *DeepRho*
DeepRho: software accompanyment for "DeepRho: Accurate Estimation of Recombination Rate from Inferred Genealogies using Deep Learning", Haotian Zhang and Yufeng Wu, manuscript, 2021.

DeepRho constructs images from population genetic data and takes advantage of the power of convolutional neural network (CNN) in image classification to etstimate recombination rate. The key idea of DeepRho is generating genetics-informative images based on inferred gene geneaologies and linkage disequilibrium from population genetic data.

# Code
`deeprho` is an open-source software developed for per-base recombination rate estimation from inferred genealogies using deep learning. `deeprho` makes estimates based on LD patterns and local genealogical trees inferred by *RENT+*[^1].

---
### Requirements
- OS: Linux(x64), Windows(x64)
- Software: [Conda](https://docs.conda.io/projects/conda/en/latest/index.html), [Git](https://git-scm.com/) (optional)

### Installation
1. Clone from GitHub using `git clone https://github.com/biotoolscoders/deeprho.git` or Download & unzip the file to your local directory. 
3. Enter the directory `cd deeprho`
4. Create a virtual environment `conda env create -f environment.yml`
5. Activate conda environment `conda activate deeprho`

Note: All dependencies are listed in `environment.yml` and their versions can be slightly modified to make them compatible with your personal settings. `java` should be already added to `$PATH` and is able to be executed anywhere in the system.

### Input formats
- MS-like format (3 example files are provided in `data/`)
- Fasta (coming soon)


### Usage
1. Run `./deeprho -f data/simulated_mu1e-8_r8.61e-8_samples100_len1e5/data.txt -w 50 -s 100 -m pretrain_models/snp50_rho200.mdl -n 100000 -l 100000 -r 1000`

2. | Arguments |       Alternative Names        |  Descriptions                                                |
   | --------- | ------------------------------ | -------------------------------------------------------------|
   | -f        | --msfile <MSFILE>              | Path of MS-format input                                      |
   | -w        | --window-size <WINDOWSIZE>     | Size for each slidding window (only 50 can be used currently)|
   | -s        | --sample-size <POPSIZE>        | Samples size                                                 |
   | -m        | --model <MODEL>                | Path of trained model                                        |
   | -n        | --effective-popsize            | Effective population size                                    |
   | -l        | --chr-length                   | Length of haplotypes in unit bp                              |
   | -r        | --resolution                   | Resoulution of recombination rates(ex. 1000 means rates/1kbp)|
   | -h        | --help                         | Show usage                                                   |
3. Type `./deeprho --help` to review usage.
  
Notes: `deeprho` should be ran directly under its root directory. As `deeprho` will generate a bunch of intermediate files inside the folder where inputs are, to avoid confliction, we strongly suggest users to create a new folder for each input file respectively.

### Results
`data/simulated_mu1e-8_r8.61e-8_samples100_len1e5/map.jpg` plots the recombination map.
   
`data/simulated_mu1e-8_r8.61e-8_samples100_len1e5/predict.txt` shows the inferred recombination map and consists of three columns specifying per-base rate and its corresponding interval. 
   
The estimated map shows like, 
|Rate(cM/Mb)	        |Start|End  |
|----------------------|-----|-----|
|6.472496479428238e-08 |30   |2626 |
|5.8559982249993625e-08|2626 |5383 |
|8.013135187014052e-08 |5383 |7686 |
|9.297690440698997e-08 |7686 |10014|
|6.951138383643149e-08 |10014|12323|
|9.179549591381548e-08 |12323|15114|
|8.611719242697401e-08 |15114|16966|
|8.797485828399659e-08 |16966|19366|
|7.588521843282585e-08 |19366|21706|


Contact Email: haotianzh@uconn.edu.
    
### Reference:
[^1]: Mirzaei S, Wu Y. RENT+: an improved method for inferring local genealogical trees from haplotypes with recombination. Bioinformatics. 2017 Apr 1;33(7):1021-1030.
  
