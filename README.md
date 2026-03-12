# Artemis
This is a data management script for old sensor data for the Artemis project.

## setup

### How to setup the python environment.
```shell
python -m .venv .
pip install -r requirements.txt
source .venv/bin/activate
```

## Run
`python src/main.py --help`

### Migrating from a directory structure to a single file per sensor.
`python src/main.py migrate`

### List all sensors.
`python src/main.py sensors`

## TODO:
- Put together all the files.
- Compare the times.
- Check the gaps.
- Accumullated data.
- InfluxDB match data.