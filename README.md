# Artemis
This is a data management script for old sensor data for the Artemis project.

## setup

### How to setup the python environment.
```shell
python -m .venv .
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```shell
source .venv/bin/activate
python src/main.py --help
deactivate
```

### Migrating from a directory structure to a single file per sensor.
`python src/main.py migrate`

### List all sensors.
`python src/main.py sensors`

## TODO:
- Put together all the files.
- Compare the times.
- Check the gaps.
- Fix summer to winter and vice versa time jumps
- Fix Accumulated histogram data.
- Export to InfluxDB.