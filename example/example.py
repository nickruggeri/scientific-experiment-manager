import re
from pathlib import Path

import numpy as np

from sem.manager import ResultManager

example_res = Path("./example_results")

# Parse directory names.
parsers = [re.compile(r"seed=(?P<seed_value>\d+)"), re.compile(r"eps_(?P<eps>\d+.\d+)")]
manager = ResultManager(root_dir=example_res, parsers=parsers)
manager.parse_paths()

# Convert parameters to different types.
manager.df["seed_value"] = manager.df["seed_value"].astype(int)
manager.df["eps"] = manager.df["eps"].astype(float)

# Load computational time and compute mean for seed 111.
def read_comp_time(res_dir):
    with open(res_dir / "computational_time.txt", "r") as file:
        time = float(file.read())
    return time


manager.df["time"] = manager.df["__PATH__"].map(read_comp_time)

df = manager.df
times = df["time"].loc[df["seed_value"] == 111]
print("Mean computational time for seed 111:", times.mean())


# Load and store a numpy matrix of parameters from the experiments.
def load_mat(path):
    return np.load(path / "result_params.npy")


df["mat"] = df["__PATH__"].map(load_mat)


# Create some example paths.
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

# Parse these paths.
manager = ResultManager.from_arguments(
    root_dir,
    arguments=[
        {"param1": "True|False", "param2": "a|b"},
        "results_of_my_experiments",
        {"param3": r"\d+"},
    ],
    auto_sort=True,
)
manager.parse_paths()
print(manager.df)

# Equivalent initialization.
parsers = [
    re.compile("param1=(?P<param1>True|False)_param2=(?P<param2>a|b)"),
    re.compile("results_of_my_experiments"),
    re.compile("param3=(?P<param3>\d+)"),
]
manager = ResultManager(root_dir, parsers)
manager.parse_paths()
