import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the images_text.csv file
image_text = pd.read_csv("image_text.csv")

# Create a DataFrame for lockers
locker_df = pd.DataFrame({"Locker": range(1, 181), "Count": 0})

# Count the number of times each locker is used
for index, row in locker_df.iterrows():
    locker = row["Locker"]
    locker_df.loc[index, "Count"] = image_text[image_text["text"] == locker].shape[0]

# Reshape data for heatmap (e.g., 15 rows x 12 columns)
heatmap_data = locker_df.pivot_table(
    index=(locker_df.index // 12),
    columns=(locker_df.index % 12),
    values="Count",
    fill_value=0,
)

print(heatmap_data)

# Plot heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True)
plt.title("Locker Usage Heatmap")
plt.xlabel("Locker Number")
plt.ylabel("Row")
plt.show()
