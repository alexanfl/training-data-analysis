import sys
import numpy as np
from pathlib import Path
import argparse
import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Constants
MAIN_LIFTS = [
        "Bench Press (Barbell)",
        "Squat (Barbell)",
        "Overhead press (Barbell)",
        "Sumo Deadlift (Barbell)",
        ]

parser = argparse.ArgumentParser(description="")
parser.add_argument("input_file", type=str, help="input data file")
parser.add_argument(
        "--print-exercises", "-p", 
        action="store_true", 
        help="display all exercises in dataset")
parser.add_argument(
        "--exercises", "-e", 
        type=int,
        nargs="+",
        help="add ")
args = parser.parse_args()

data_filepath = Path(args.input_file)
out_folder = Path("../out")
out_folder.mkdir(exist_ok=True)


# Use seaborn style defaults and set the default figure size
sns.set(rc={"figure.figsize":(11, 4)})


def calculate_1rm_epley(w: float, r: int):
    """Calculates estimated 1 RM using the Epley formula

    weight w for r reps.
    """

    if r == 1:
        return w
    if r == 0:
        return 0

    return w*(1 + r/30)


def main():
    df = pd.read_csv(data_filepath, sep=";")
    df["Date"] = pd.to_datetime(df["Date"])
    unique_exercises = list(df["Exercise Name"].value_counts().index)

    if args.print_exercises:
        for i,ex in enumerate(unique_exercises):
            print(f"{i}: {ex}")
        sys.exit()

    if not args.exercises:
        exercises = MAIN_LIFTS
    else:
        exercises = [unique_exercises[i] for i in args.exercises]

    for ex in exercises:
        df_ex = df.loc[df["Exercise Name"] == ex]
        df_ex.set_index("Date", inplace=True)
        df_ex.loc[:, "Set Volume"] = df_ex["Weight"]*df_ex["Reps"]

        grouper1 = df_ex.groupby("Date")
        d1 = grouper1["Set Volume"].sum().to_frame(
                name="Total Volume").reset_index()

        df_ex["Est. 1 RM"] = df_ex.apply(
                lambda x: calculate_1rm_epley(x["Weight"], x["Reps"]), axis=1)
        grouper2 = df_ex.groupby("Date")
        d2 = grouper2["Est. 1 RM"].max().to_frame(
                name="Est. 1 RM").reset_index()

        d2["Total Volume"] = d1["Total Volume"]

        axes = d2[["Est. 1 RM", "Total Volume"]].plot(
                title=ex,
                marker=".", 
                linewidth=0.5, 
                alpha=0.5, 
                linestyle="None", 
                figsize=(11, 9), 
                subplots=True)
        plt.savefig(
                out_folder / f"{ex}_{data_filepath.with_suffix('.png').name}")
        plt.show()

if __name__ == "__main__":
    main()
