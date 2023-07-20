import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import json
import numpy as np
from scipy.stats import entropy

# Load the data
with open("data/maia_predictions.json", "r") as file:
    data = json.load(file)

# Function to calculate entropy
def calculate_entropy(distribution):
    # Get the probabilities
    probabilities = list(distribution.values())
    # Calculate and return the entropy
    return entropy(probabilities, base=2)

# Filter entries with len(moves) == 0
data = [position for position in data if len(position["maia-1100"]["moves"]) > 0 and len(position["maia-1900"]["moves"]) > 0]

# Calculate the entropy for each position and each Maia version
entropy_values = []
for position in data:
    fen = position["fen"]
    for maia_version, predictions in position.items():
        if maia_version != "fen":
            entropy_value = calculate_entropy(predictions["moves"])
            entropy_values.append({"fen": fen, "maia_version": maia_version, "entropy": entropy_value})

# Convert the data to a Pandas DataFrame
df = pd.DataFrame(entropy_values)

# Separate the data for the two Maia versions
df_1100 = df[df["maia_version"] == "maia-1100"]
df_1900 = df[df["maia_version"] == "maia-1900"]


# Calculate the standard deviation and median of the entropy for each Maia version
std_1100 = df_1100["entropy"].std()
std_1900 = df_1900["entropy"].std()
median_1100 = df_1100["entropy"].median()
median_1900 = df_1900["entropy"].median()

# Create the plots
plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
sns.histplot(df_1100["entropy"], color="blue", kde=True)
plt.title("Entropy Distribution for Maia-1100")
plt.xlabel("Entropy")
plt.ylabel("Frequency")

plt.subplot(1, 2, 2)
sns.histplot(df_1900["entropy"], color="green", kde=True)
plt.title("Entropy Distribution for Maia-1900")
plt.xlabel("Entropy")
plt.ylabel("Frequency")

plt.tight_layout()
plt.show()

print(std_1100, median_1100, std_1900, median_1900)