import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns

# Use seaborn style defaults and set the default figure size
sns.set(rc={'figure.figsize':(11, 4)})

def calculate_1rm_epley(w, r):
    """
    Calculates estimated 1 RM using the Epley formula.
    weight w for r reps.
    """

    if r == 1:
        return w
    if r == 0:
        return 0

    return w*(1 + r/30)

def get_est_1rm_by_date(data):
    est_1rm_by_date = {}

    for row in data.itertuples():
        date = row.Date
        if date in est_1rm_by_date:
            est_1rm_by_date[date] = max(est_1rm_by_date[date],
                                            calculate_1rm_epley(row.Weight, row.Reps))
        else:
            est_1rm_by_date[date] = calculate_1rm_epley(row.Weight, row.Reps)

    return est_1rm_by_date

def get_total_volume_by_date(data):
    total_volume_by_date = {}

    for row in data.itertuples():
        date = row.Date
        if date in total_volume_by_date:
            total_volume_by_date[date] += row.Weight*row.Reps
        else:
            total_volume_by_date[date] = row.Weight*row.Reps

    return total_volume_by_date

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file", type=str, help="input data file")
    args = parser.parse_args()

    data_filepath = Path(args.input_file)
    out_folder = Path("../out")
    out_folder.mkdir(exist_ok=True)

    df = pd.read_csv(data_filepath, sep=";")
    df["Date"] = pd.to_datetime(df["Date"])

    df_all_dates = pd.date_range(min(df["Date"]), max(df["Date"]), freq="D")
    all_exercises = df["Exercise Name"].unique()

    column_names = []
    for exercise_name in all_exercises:
        column_names.append("Est. 1 RM - " + exercise_name)
        column_names.append("Total Volume - " + exercise_name)

    df_all_exercises = pd.DataFrame(columns=column_names)
    df_all_exercises = df_all_exercises.assign(Date=df_all_dates)

    df_dict = {
            "Overhead Press": df.loc[df["Exercise Name"] == "Overhead Press (Barbell)"],
            "Squat": df.loc[df["Exercise Name"] == "Squat (Barbell)"],
            "Sumo Deadlift": df.loc[df["Exercise Name"] == "Sumo Deadlift (Barbell)"],
            "Bench Press": df.loc[df["Exercise Name"] == "Bench Press (Barbell)"],
    }
    new_df_dict = {}

    for key, val in df_dict.items():
        est_1rm_by_date = get_est_1rm_by_date(val)
        total_volume_by_date = get_total_volume_by_date(val)
        new_df_dict[key] = pd.DataFrame({
                    "Date": [d for d in est_1rm_by_date],
                    "Est. 1 RM": [est_1rm_by_date[d] for d in est_1rm_by_date],
                    "Total Volume": [total_volume_by_date[d] for d in total_volume_by_date],
                })

    print(df_all_exercises)

    data_columns_est_1rm = ["Est. 1 RM Squat", 
					"Est. 1 RM Sumo Deadlift", 
					"Est. 1 RM Overhead Press", 
					"Est. 1 RM Bench Press"]

    data_columns_volume = ["Total Volume Squat", 
						   "Total Volume Sumo Deadlift", 
					       "Total Volume Overhead Press", 
					       "Total Volume Bench Press"]

    for key, val in df_dict.items():
        est_1rm_by_date = get_est_1rm_by_date(val)
        total_volume_by_date = get_total_volume_by_date(val)
        new_df_dict[key] = pd.DataFrame({
                    "Date": [d for d in est_1rm_by_date],
                    "Est. 1 RM": [est_1rm_by_date[d] for d in est_1rm_by_date],
                    "Total Volume": [total_volume_by_date[d] for d in total_volume_by_date],
                })


    merged_df = new_df_dict["Squat"].merge(new_df_dict["Sumo Deadlift"], on="Date", how="outer", suffixes=(" Squat", " Sumo Deadlift")).merge(new_df_dict["Bench Press"], on="Date", how="outer").merge(new_df_dict["Overhead Press"], on="Date", how="outer", suffixes=(" Bench Press", " Overhead Press"))

    workouts_daily = merged_df.sort_values(by="Date")
    workouts_daily = workouts_daily.set_index("Date")

    axes = workouts_daily[data_columns_est_1rm].plot(marker='.', linewidth=0.5, alpha=0.5, linestyle='None', figsize=(11, 9), subplots=True)
    plt.savefig(out_folder / ("Est_1rm_" + data_filepath.with_suffix(".png").name))

    axes = workouts_daily[data_columns_volume].plot(marker='.', linewidth=0.5, alpha=0.5, linestyle='None', figsize=(11, 9), subplots=True)
    plt.savefig(out_folder / ("Tot_vol_" + data_filepath.with_suffix(".png").name))
	

if __name__ == "__main__":
    main()
