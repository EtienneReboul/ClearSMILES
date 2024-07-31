<h1>ClearSMILES</h1>

<p>ClearSMILES is a data augmentation procedure for SMILES. The first goal of CLearSMILES is to minimize the dimensionality of SMILES, i.e., reducing the size of the vocabulary needed to describe a dataset. The second goal of ClearSMILES is to reduce the attention effort a machine learning model has to make to process a SMILES.</p>

<h2>How to install ClearSMILES</h2>

<p>First, clone the repository:</p>

<pre><code>git clone https://github.com/EtienneReboul/ClearSMILES.git
cd ClearSMILES/
</code></pre>

<p>To install the python dependencies, you can create a virtual env:</p>

<pre><code>pip install virtualenv
virtualenv ClearSMILES_env
source ClearSMILES_env/bin/activate
pip install requirements.txt
</code></pre>

<p>or</p>

<p>you can install using conda:</p>

<pre><code>conda env create -f ClearSMILES_environement.yml
</code></pre>

<h2>How to download MOSES dataset</h2>

<p>The MOSES dataset can be easily downloaded using the following code:</p>

<pre><code>python src/data/download_moses.py
</code></pre>

<p>The default argument should download the MOSES dataset as whole_original_MOSES.csv in the data/raw directory. You might want to check that the default link to MOSES is still viable using the following:</p>

<pre><code>pytest src/test/download_test.py
</code></pre>

<h2>How to generate ClearSMILES for MOSES</h2>

<p>ClearSMILES is a stochastic data augmentation procedure. Therefore, it is not possible to guarantee that it will always yield the same results. However, by generating a very large number of SMILES, the default setting is 100k randomized SMILES per molecule, the results should be somewhat consistent. As random search is a time-consuming process, the ClearSMILES generation process is conceived to be parallelized on a cluster. Here is an example of a SLURM job on how to do that:</p>

<pre><code>#!/bin/sh
#SBATCH --time=01:00:00
#SBATCH --job-name=ClearSMILES_gen
#SBATCH --output=logs/ClearSMILES_gen/out_%A_%a.log
#SBATCH --error=logs/ClearSMILES_gen/err_%A_%a.log
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --array=1-2000

# activate virtualenv
source ClearSMILES_env/bin/activate

# launch script
python src/features/generate_clearsmiles.py  --input_csv data/raw/whole_original_MOSES.csv\
 --output_filepath  data/interim/ClearSMILES_MOSES_subset_${SLURM_ARRAY_TASK_ID}.parquet --task_id $SLURM_ARRAY_TASK_ID\
 --job_array_size 2000 --nb_random 100000 --nb_smiles 1936962
</code></pre>

<p>If you want to use a custom dataset, you need first to give the path to your custom dataset like so: data/raw/custom_dataset.csv. Note that your custom dataset needs to be a CSV file with a ',' as the separator, and the SMILES column should be named 'SMILES' with uppercase. To prevent name collision for the output files, we strongly support using the task ID of the SLURM array to index them. The <code>--nb_smiles</code> should be the number of SMILES, i.e., the number of molecules in your dataset. The task ID and the job array size are used to retrieve the chunk of data to be processed. If you do not want to use a job array (not recommended), you can put <code>--task_id 0</code> and <code>--job_array_size 1</code> to compute all ClearSMILES at once. The flag <code>--nb_random</code> is the number of randomized SMILES that will be generated to search for the best ClearSMILES.</p>

<h2>Aggregating data and relaunching failed jobs</h2>

<p>First, you need to check if all the jobs have successfully completed using:</p>

<pre><code>python src/features/get_failed_gen_tasks.py --search_pattern data/interim/ClearSMILES_MOSES_subset_*.parquet --output_filepath data/external/failed_task_id.txt
</code></pre>

<p>Adjust the search pattern accordingly for a custom dataset. If all tasks were executed successfully, you will get the following message: 'all tasks were successfully completed, no file will be written'. Otherwise, a success rate will be printed, and all the failed task IDs will be written on one line in the output file. After checking the logs for what went wrong, you can relaunch the jobs by replacing the parameter SLURM array range for the ClearSMILES generation like so:</p>

<p>e.g., <code>#SBATCH --array=1-2000</code> -&gt; <code>#SBATCH --array=3,15,42,1457</code></p>

<p>When all the tasks are completed, you aggregate all the data to a single file using:</p>

<pre><code>python src/features/concatenate2lib.py --search_pattern data/interim/ClearSMILES_MOSES_subset_*.parquet --output_filepath data/processed/whole_MOSES_ClearSMILES_results.parquet
</code></pre>

<p>You can use multiprocessing to read the file via the use of the flag <code>--use_multiprocessing</code>.</p>

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

