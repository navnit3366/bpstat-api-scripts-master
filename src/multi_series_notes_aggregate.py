#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Modify multiple series from Bank of Portugal's statistics API and plot their sum.
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

# Convert the note quantities in millions of euros:
face_re = re.compile(r"^([0-9]+)\s+euros$", re.IGNORECASE)
dataframe[face_value_label] = pandas.to_numeric(dataframe[face_value_label].map(lambda n: int(face_re.match(n)[1])))
dataframe["value"] = (dataframe["value"] * dataframe[face_value_label]) / 1_000_000

# Sum all the amounts into a single series:
columns = dataframe[[time_label, "value"]]
columns = columns.groupby(time_label).sum()
columns = columns.reset_index()  # ...make the group a regular column.

unit = {
    "EN": "Millions of euros",
    "PT": "Milhões de euros"
}

title = {
    "EN": "Counterfeit banknotes withdrawn from circulation in Portugal (M€)",
    "PT": "Notas falsas retiradas de circulação em Portugal (M€)"
}

# Plot the data, with proper labels and titles:
plot = columns.plot(kind="line", x=time_label, y="value", figsize=(10, 5), style="o:", legend=False)
plot.set(title=title[LANGUAGE], xlabel=f"{time_label} ({dataframe[recurrence_label][0]})", ylabel=unit[LANGUAGE])

# Show an axis grid in the background:
plot.set_axisbelow(True)
plot.grid("on", which="major", axis="y", linestyle="dotted", linewidth=0.5)
plot.set_ylim(bottom=0)

pyplot.show()


# EOF
