<h2 align="center"><i>SEM</i>: Scientific Experiment Manager</h2>
<p align="center"><i>Streamline IO operations, storage, and retrieval of your scientific results</i></p>

<p align="center">
<a href="https://github.com/nickruggeri/scientific-experiment-manager/blob/main/LICENSE">
<img alt="License: MIT" src="https://img.shields.io/github/license/nickruggeri/scientific-experiment-manager">
</a>
<a href="https://www.python.org/">
<img alt="Made with Python" src="https://img.shields.io/badge/made%20with-python-1f425f.svg">
</a>
<a href="https://github.com/psf/black">
<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</a>
</p>


SEM helps streamline IO operations and organization of scientific results
in Python. \
At its core, SEM is based on 
[regular expressions](https://docs.python.org/3/library/re.html) 
and simply creates, parses and manages intricate folder structures containing 
experimental results.  

<br/><br/>
## Minimal example
Consider the results organized in the `example/example_results` folder. \
These are different directories containing the results of the same experiment, where two
parameters are varied: the random `seed` and a threshold value `eps`. Every one of the 
folders contains some output files from  
```
example_results
│
└───seed=111
│   └───eps_1.3
│   │   └───...
│   └───eps_7.4
│       └───...
│   
└───seed=222
│   └───...
│
└───seed=333
│   └───...
│   
└───useless_files
```
SEM does not take care of loading and/or saving files. \
Rather, it takes care of the folder structure, leaving the user the freedom to manage the result's 
format. \
To retrieve the parameters relative to these results, `ResultManager` parses the folders'
names and only returns the path relative to those that match. 
```python
import re
from pathlib import Path

from sem.manager import ResultManager

example_res = Path("./example_results")

parsers = [re.compile(r"seed=(?P<seed_value>\d+)"), re.compile(r"eps_(?P<eps>\d+.\d+)")]
manager = ResultManager(root_dir=example_res, parsers=parsers)
manager.parse_paths()
```
In the case above, the parser for `seed_value` expects a positive integer, specified by 
the regular expression `"\d+"`, and `eps` a float format. \
The results are stored in 
`manager.df`, a pandas 
[DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html), which 
contains the parsed parameter values, as well as the path to the deepest sub-directories  
```
                           __PATH__ seed_value  eps
0  example_results/seed=333/eps_1.1        333  1.1
1  example_results/seed=333/eps_0.3        333  0.3
2  example_results/seed=222/eps_7.4        222  7.4
3  example_results/seed=222/eps_2.7        222  2.7
4  example_results/seed=111/eps_1.3        111  1.3
5  example_results/seed=111/eps_7.4        111  7.4
...
```
Directories whose names don't match the patterns are ignored, e.g. 
`example_results/useless_files`. \
Notice that, since they are the results of parsing, all the values in the data frame are
strings. \
The conversion to a different data type can be performed after parsing:
```python
manager.df["seed_value"] = manager.df["seed_value"].astype(int)
manager.df["eps"] = manager.df["eps"].astype(float)
```

### Utilizing the parsed directories
Once the directory names have been parsed, the main utility of the manager is to have a 
coupling between the parameters and the results. \
For example, one can read and insert the computational time of every experiment in the 
data frame:
```python
def read_comp_time(res_dir):
    with open(res_dir / "computational_time.txt", "r") as file:
        time = float(file.read())
    return time


manager.df["time"] = manager.df["__PATH__"].map(read_comp_time)
```
From there, conventional pandas operations can be used. For example, the average 
computational time for seed `111` is given by
```python
df = manager.df
times = df["time"].loc[df["seed_value"] == 111]
times.mean()
```

### Loading more complex objects
Pandas data frames can contain arbitrary objects. 
For example, one can create a column of numpy arrays from a model:
```python
import numpy as np


def load_mat(path):
    return np.load(path / "result_params.npy")


df["mat"] = df["__PATH__"].map(load_mat)
```

<br/><br/>
## Creating default paths
Standardizing result structure reduces the amount of code needed for 
simple IO operations, and eases compatibility across machines, e.g. local vs cloud or 
cluster results. \
To this end, <i>SEM</i> offers a way to create saving paths 
which only depend on the parameters specified by the user. \
For example, the paths of a repository with three levels and different parameters, 
can be created as:
```python
root_dir = Path(".") / "tmp"
for param1 in [True, False]:
    for param2 in ["a", "b"]:
        for param3 in [1, 2, 3]:
            values = [
                {"param1": param1, "param2": param2},
                "results_of_my_experiments",
                {"param3": param3},
            ]
            new_path = ResultManager.create_default_path(
                root_dir, values, auto_sort=True
            )
            new_path.mkdir(parents=True)
            print(new_path)
```
which produces
```
tmp/param1=True_param2=a/results_of_my_experiments/param3=1
tmp/param1=True_param2=a/results_of_my_experiments/param3=2
tmp/param1=True_param2=a/results_of_my_experiments/param3=3
tmp/param1=True_param2=b/results_of_my_experiments/param3=1
...
tmp/param1=False_param2=a/results_of_my_experiments/param3=1
...
```
If desired, the argument `auto_sort` imposes a uniform order at every directory level.\
For example, using
`{"param2": param2, "param1": param1}` would produce the same paths a above if
`auto_sort=True`. \
Parsing directories with this structure is similarly easy:
```python
manager = ResultManager.from_arguments(
    root_dir,
    arguments=[
        {"param1": "True|False", "param2": "a|b"},
        "results_of_my_experiments",
        {"param3": r"\d+"},
    ],
    auto_sort=True
)
manager.parse_paths()
```
which yields
```
                                             __PATH__ param1 param2 param3
0   tmp/param1=False_param2=b/results_of_my_experi...  False      b      1
1   tmp/param1=False_param2=b/results_of_my_experi...  False      b      3
2   tmp/param1=False_param2=b/results_of_my_experi...  False      b      2
3   tmp/param1=True_param2=b/results_of_my_experim...   True      b      1
...
```

<br/><br/>
## Initialization
Notice that the advantage of using the default directory naming, as opposed to a custom
one, is that the `ResultManager` can be initialized as above, by only specifying the 
arguments in `ResultManager.from_arguments`. \
A more flexible initialization for custom paths, can be performed by giving as input 
regular expression patterns. For example, an equivalent initialization to that above is 
given by: 

```python
parsers = [
    re.compile("param1=(?P<param1>True|False)_param2=(?P<param2>a|b)"),
    re.compile("results_of_my_experiments"),
    re.compile("param3=(?P<param3>\d+)"),
]
manager = ResultManager(root_dir, parsers)
manager.parse_paths()
```

<br/><br/>
## Other utilities and tricks
### Filtering results
Another useful `ResultManager` method is `ResultManager.filter`. This method filters the
<i>rows</i> of the results' data frame. Results can be selected by specifying exact 
column values or a list of possible values. For example, for a manager whose data frame 
has columns
```
                                             __PATH__ param1 param2 param3
0   tmp/param1=False_param2=b/results_of_my_experi...  False      b      1
1   tmp/param1=False_param2=b/results_of_my_experi...  False      b      3
2   tmp/param1=False_param2=b/results_of_my_experi...  False      b      2
3   tmp/param1=True_param2=b/results_of_my_experim...   True      b      1
...
```
the query
```python
manager.filter_results(
    equal={"param1": True},
    contained={"param3": [1, 3]}
)
```
yields a filtered data frame
```
                                             __PATH__ param1 param2 param3
3   tmp/param1=True_param2=b/results_of_my_experim...   True      b      1
4   tmp/param1=True_param2=b/results_of_my_experim...   True      b      3
9   tmp/param1=True_param2=a/results_of_my_experim...   True      a      1
10  tmp/param1=True_param2=a/results_of_my_experim...   True      a      3
```

### Loading fewer results
While results can be filtered a posteriori as just explained, one can also load fewer 
results in the first place. \
This is done by specifying an appropriate regular expression 
parser in the first place.  
For example, to select only configurations where 
`param1` is equal to `True`, one can write
```python
parsers = [
    re.compile("param1=(?P<param1>True)_param2=(?P<param2>a|b)"),
    re.compile("results_of_my_experiments"),
    re.compile("param3=(?P<param3>\d+)"),
]
manager = ResultManager(root_dir, parsers)
```
In general, any regular expression with named groups is considered valid, check 
[the docs](https://docs.python.org/3/library/re.html) 
for further details. 

### Common parsing patterns
Some common regular expression patterns are available at `sem.re_patterns`. \
These are strings that can be utilized for initializing parsers 
```python
from sem.re_patterns import INT_PATTERN

parsers = [
    re.compile("param1=(?P<param1>True|False)_param2=(?P<param2>a|b)"),
    re.compile("results_of_my_experiments"),
    re.compile(f"param3=(?P<param3>{INT_PATTERN})"),
]
manager = ResultManager(root_dir, parsers)
```
or `ResultManager` arguments
```python
manager = ResultManager.from_arguments(
    root_dir,
    arguments=[
        {"param1": "True|False", "param2": "a|b"},
        "results_of_my_experiments",
        {"param3": INT_PATTERN},
    ],
)
```


### Common type conversion from string
Some common type conversion functions from string are available at `sem.str_to_type`. \
These are useful in combination with the `argparse` package, for command line inputs
```python
from argparse import ArgumentParser
from sem.str_to_type import bool_type, unit_float_or_positive_integer, none_or_type

parser = ArgumentParser()    
parser.add_argument("--flag", type=bool_type)
parser.add_argument("--train_size", type=unit_float_or_positive_integer)
parser.add_argument("--K", type=none_or_type(int))
```
Importantly, `bool_type` correctly converts both string inputs `"0"` or `"1"`, as well 
as the case-insensitive strings `"true"`, `"True"`, `"False"`, etc. 


Alternatively, these functions can also be used for type conversion inside pandas data 
frames
```python
manager = ResultManager(root_dir, parsers)
manager.parse_paths()

manager.df["flag"] = manager.df["flag"].map(bool_type)
```

<br/><br/>
## Installation
You can install this package by downloading the GitHub repository and, from inside the
downloaded folder, running
```
pip install .
```
