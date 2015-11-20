# Cowfish
Cowfish is an Aquarium cytometry results analyzing software package written in Python.

## Installation

```
git clone https://github.com/klavinslab/cowfish.git
cd cowfish
pip install .
```

## How to use

### Importing and initialization

```
from cowfish import Cowfish
co = Cowfish(aquarium_url/api, aquarium_login, aquarium_api_key, local_folder_path_to_store_downloads)
```

An example of initialization is as follows:

```
co = Cowfish("http://54.68.9.194:81/api", "yang", "Xqebo0lhbQ_grN8l9ZlEF1rC_bDIsyqfh74pOgwcNzQ",r'/Users/yaoyu/Dropbox/Yaoyu_SOSLab_Research/Aquarium_cytometry/')
```

## Aquarium cytometry job data summary

An example:
```
df_singlets = co.cytometry_results_summary([job_id_1,job_id_2,job_id_3], ploidy="haploid", only='singlets')
```
This will process the cytometry results in job_id_1, job_id_2, and job_id_3, pass through yeast haploid and singlets gate and return a [Pandas](http://pandas.pydata.org/) dataframe (a table like data structure but much more powerful thanks to Pandas) that summarizing all the results with time, sample_name, fluorescence value, concentration.

## Dependencies

### python 2.7:

* [scipy](http://www.scipy.org/)
* [matplotlib](http://matplotlib.org/)
* [pandas](http://pandas.pydata.org/)
* [FlowCytometryTools](http://eyurtsev.github.io/FlowCytometryTools/install.html)
* [aquarium-api-python](https://github.com/klavinslab/aquarium-api-python)
