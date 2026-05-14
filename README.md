# Artemis
Artemis is an EU sponsored radon measurement project with the aim of gathering measurements from sensors placed in various locations of importance to seismology. This repository is for data management and recovery script for old sensor data measurements.

### What are these scripts about
These scripts provides the means to list each sensor data in a single file and processes the existing timestamps while also recovering the missing timestamps by statistical means and finally exporting the data to an InfluxDB instance.

## How to

### Setup
First setup python environment and install the dependencies:
```shell
python -m .venv .
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
To list available commands:
```shell
./artemis --help
```

or using python directly:
```shell
source .venv/bin/activate
python src/main.py --help
deactivate
```

#### Run All
Run data recovery and export to InfluxDB all in one command.
```shell
./artemis recoverAndMigrate
```

## Class diagram
![Alt text](KEX_Class_diagram.drawio.svg)

## TODO:
- [x] Put together all the files of a single sensor.
- [x] Fix DST time overlaps and time jumps.
- [x] Flatten accumulated histogram data.
- [x] Recover missing timestamps.
- [x] Export to InfluxDB.
- [x] UML Class diagram.