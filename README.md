# What is this?

The [portuguese central bank](https://www.bportugal.pt) provides an open statistics API at [https://bpstat.bportugal.pt/data/docs/](https://bpstat.bportugal.pt/data/docs/) and this repository contains some scripts that fetch data from it, which can be used as starting points for more elaborate purposes.

This is unofficial example code, written for my own amusement, which may break over time as the API evolves. They're all in Python, which is my programming language of choice.

## Requirements

Assuming you have Python (>= 3.6) and Git already installed, just run the following commands to clone this repository and create a virtual environment with the necessary dependencies:
```
$ git clone git@github.com:carlosefr/bpstat-api-scripts.git
$ cd bpstat-api-scripts
$ make
$ . bpstat-venv/bin/activate
```

Then run an example to confirm it's all OK:
```
$ src/single_series_gdp.py
```

You can deactivate the virtual environment in your terminal session at any time with:
```
$ deactivate
```

Or, just closing the terminal window will suffice. :)

## Examples

* [`single_series_gdp.py`](https://github.com/carlosefr/bpstat-api-scripts/blob/master/src/single_series_gdp.py): Fetch a single timeseries for the portuguese GDP and use its metadata to add proper labels to the graph. ![single_series_gdp.png](https://raw.githubusercontent.com/carlosefr/bpstat-api-scripts/master/screenshots/single_series_gdp.png)

* [`multi_series_notes.py`](https://github.com/carlosefr/bpstat-api-scripts/blob/master/src/multi_series_notes.py): Fetch multiple timeseries for counterfeit banknotes in a single call and plot them together in the same graph. ![multi_series_notes.png](https://raw.githubusercontent.com/carlosefr/bpstat-api-scripts/master/screenshots/multi_series_notes.png)

* [`multi_series_notes_aggregate.py`](https://github.com/carlosefr/bpstat-api-scripts/blob/master/src/multi_series_notes_aggregate.py): Fetch the same banknote timeseries as above, but this time aggregate their data into a new timeseries (in euros, instead of number of banknotes). ![multi_series_notes_aggregate.png](https://raw.githubusercontent.com/carlosefr/bpstat-api-scripts/master/screenshots/multi_series_notes_aggregate.png)
