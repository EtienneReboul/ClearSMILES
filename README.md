ClearSMILES
==============================

ClearSMILES is a data augmentation procedure for SMILES. The first goal of CLearSMILES is to minimize the dimensionality of SMILES
i.e reducing the size of the vocabulary needed to describe a dataset. The second goal of ClearSMILES is to reduce the attention effort
a machine learning has to make to process a SMILES.

How to install ClearSMILES
------------
first clone the repository :
```
git clone https://github.com/EtienneReboul/ClearSMILES.git
cd ClearSMILES/
```

To install the python dependencies , you can create a virtual env:
```
pip install virtualenv
virtualenv ClearSMILES
source ClearSMILES/bin/activate
pip install requirements.txt

```

or 

you can install using conda :

```
conda env create -f ClearSMILES_environement.yml

```
--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
