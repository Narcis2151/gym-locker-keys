from collections import Counter
import pandas as pd


def generate_heatmap(locker_numbers, nr_lockers=162):
    locker_numbers = [int(i) for i in locker_numbers]
    locker_counts = Counter(locker_numbers)

    # Create a DataFrame for lockers
    locker_df = pd.DataFrame(
        {
            "Locker": range(1, nr_lockers + 1),
            "Count": [locker_counts.get(i, 0) for i in range(1, nr_lockers + 1)],
        }
    )

    # Reshape data for heatmap (e.g., 18 rows x 9 columns)
    heatmap_data = locker_df.pivot_table(
        index=(locker_df.index // 9),
        columns=(locker_df.index % 9),
        values="Count",
        fill_value=0,
    )
    return heatmap_data
