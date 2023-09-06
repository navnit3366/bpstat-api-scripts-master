#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Plot a lone series from Bank of Portugal's statistics API.
#
# Note: This code is meant as an example and, in order to
#       maximize readability, lacks proper error handling.
#
# Carlos Rodrigues <cefrodrigues@gmail.com>
#

import time
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
REFERENCE_TERRITORY_DIMENSION_ID = "63"


#
# Portuguese GDP at market prices in millions of euros:
# https://bpstat.bportugal.pt/serie/12518356
#
series_id = "12518356"

#
# Series data is contained in a statistics domain dataset and we must figure out which
# dataset that is. In this case (single series) it doesn't matter which domain we use,
# as long as it is one of the domains where the series is present.
#
print("Fetching series metadata...")
series_url = f"{BPSTAT_API_URL}/series/?lang={LANGUAGE}&series_ids={series_id}"
series_metadata = requests.get(series_url).json()[0]  # ...there is only one series.

domain_id = series_metadata["domain_ids"][0]  # ...just select the first statistics domain of the series.
dataset_id = series_metadata["dataset_id"]  # ...the dataset will contain the actual data for the series.

# Fetch the series values over time (observations), in JSON-stat format:
print("Fetching series observations...")
dataset_url = f"{BPSTAT_API_URL}/domains/{domain_id}/datasets/{dataset_id}/?lang={LANGUAGE}&series_ids={series_id}"
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

    if dimension_id == REFERENCE_TERRITORY_DIMENSION_ID:
        reference_territory_label = dimension["label"]
        continue

# Convert dates to a proper pandas date format:
dataframe[time_label] = pandas.to_datetime(dataframe[time_label])

# Select the data to plot:
columns = dataframe[[time_label, "value"]]

# Plot the data, with proper labels and titles:
plot = columns.plot(kind="line", x=time_label, y="value", figsize=(10, 5), style="o:")

# We want to use the categories' names, not their dimensions'...
recurrence_category = dataframe[recurrence_label][0]
unit_category = dataframe[unit_label][0]
reference_territory_category = dataframe[reference_territory_label][0]

plot.set(title=series_metadata["label"], xlabel=f"{time_label} ({recurrence_category})", ylabel=unit_category)
plot.legend([reference_territory_category])

# Show an axis grid in the background:
plot.grid("on", which="major", axis="y", linestyle="dotted", linewidth=0.5)
plot.set_axisbelow(True)
plot.set_xlim(right=pandas.Timestamp(time.time(), unit="s"))

pyplot.show()


# EOF
