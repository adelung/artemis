# Artemis deploy
Deployment for test purposes.

## Setup
This will deploy an influxDB with grafana and a ui manager.

```shell
mkdir data plugins ui_db ui_config
sudo chown 1500:1500 data plugins ui_db ui_config
docker-compose up -d
```