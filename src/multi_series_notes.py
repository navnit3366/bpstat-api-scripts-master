#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Plot multiple series from Bank of Portugal's statistics API.
#
# Note: This code is meant as an example and, in order to
#       maximize readability, lacks proper error handling.
#
# Carlos Rodrigues <cefrodrigues@gmail.com>
#

import re
import requests
import pandas

from pyjstat import pyjstat
from matplotlib import pyplot


# The base address for all BPstat API calls:
BPSTAT_API_URL = "https://bpstat.bportugal.pt/data/v1"
LANGUAGE = "EN"

# We'll use these dimensions as labels. The IDs are reliable and should always
# be defined as strings, not integers, as not all dimension IDs are numeric.
UNIT_DIMENSION_ID = "70"
RECURRENCE_DIMENSION_ID = "40"
FACE_VALUE_DIMENSION_ID = "71"


# Counterfeit euro banknotes withdrawn from circulation (in Portugal), individual denominations:
series_ids = ["12468944", "12468945", "12468946", "12468947", "12468948", "12468949", "12468950"]

#
# Series data is contained in a statistics domain dataset and we must figure out which
# dataset that is. In this case (closely related series) it doesn't matter which domain
# we use, as long as it is one of the domains where all the series are present.
#
print("Fetching series metadata...")
series_ids_str = ",".join(series_ids)
series_url = f"{BPSTAT_API_URL}/series/?lang={LANGUAGE}&series_ids={series_ids_str}"
series_metadata = requests.get(series_url).json()

domain_id = series_metadata[0]["domain_ids"][0]  # ...just select the first statistics domain of the series.
dataset_id = series_metadata[0]["dataset_id"]  # ...the dataset will contain the actual data for the series.

# In this case, we know all series are closely related:
assert all(domain_id in s["domain_ids"] for s in series_metadata)
assert all(dataset_id == s["dataset_id"] for s in series_metadata)

# Fetch the series values over time (observations), in JSON-stat format:
print("Fetching series observations...")
dataset_url = f"{BPSTAT_API_URL}/domains/{domain_id}/datasets/{dataset_id}/?lang={LANGUAGE}&series_ids={series_ids_str}"
dataset_data = pyjstat.Dataset.read(dataset_url)

print("Processing data...")

# Convert it into a pandas dataframe:
dataframe = dataset_data.write("dataframe")

#
# Now we need to figure out the names of the columns, which are language-dependent and may change over time.
#

# The time dimension is "easy" as JSON-stat provides a role to find it:
time_dimension_id = dataset_data["role"]["time"][0]   # ...there's only one.
time_label = dataset_data["dimension"][time_dimension_id]["label"]

# Other dimensions are trickier, but we can search based on their IDs:
for dimension_id, dimension in dataset_data["dimension"].items():
    if dimension_id == UNIT_DIMENSION_ID:
        unit_label = dimension["label"]
        continue

    if dimension_id == RECURRENCE_DIMENSION_ID:
        recurrence_label = dimension["label"]
        continue

    if dimension_id == FACE_VALUE_DIMENSION_ID:
        face_value_label = dimension["label"]
        continue

# Convert dates to a proper pandas date format:
dataframe[time_label] = pandas.to_datetime(dataframe[time_label])

# We will plot the series together in one chart:
figure = pyplot.figure(figsize=(10, 5))
subplot = figure.add_subplot(1, 1, 1)

# We want to use the categories' names in the chart, not their dimensions'...
recurrence_category = dataframe[recurrence_label][0]
unit_category = dataframe[unit_label][0]

title = {
    "EN": "Counterfeit banknotes withdrawn from circulation in Portugal",
    "PT": "Notas falsas retiradas de circulação em Portugal"
}

subplot.set(title=title[LANGUAGE], xlabel=f"{time_label} ({recurrence_category})", ylabel=unit_category)

# Sort the banknotes' face value to be able to use it to sort the dataframe (just because we can):
face_value_re = re.compile(r"^([0-9]+)\s+euros$", re.IGNORECASE)
face_values = {label: int(face_value_re.match(label).group(1)) for label in set(dataframe[face_value_label].values)}
sorted_face_values = [label for label, _ in sorted(face_values.items(), key=lambda item: item[1])]

# Now actually sort the dataframe by banknotes' face value...
dataframe[face_value_label] = pandas.Categorical(dataframe[face_value_label], sorted_face_values)
dataframe.sort_values(face_value_label)

legends = []

# Split the dataframe by banknote face value and add each one to the chart:
for face_value_category, group in dataframe.groupby(face_value_label):
    subplot.plot(group[time_label], group["value"], marker=".", linestyle="solid", linewidth=1.0)
    legends.append(face_value_category)

# Show an axis grid in the background:
subplot.grid("on", which="major", axis="y", linestyle="dotted", linewidth=0.5)
subplot.set_axisbelow(True)

figure.legend(legends)

pyplot.show()


# EOF
