import typer
from data_service import DataService

app = typer.Typer()
dataService = DataService()


@app.command()
def collectToFile(
    dataPath="./data",
):
    dataService.migrateDirectoryToFile(dataPath)


@app.command()
def collectToCleanData(
    dataPath="./data",
):
    dataService.migrateDirectoryToCleanData(dataPath)


@app.command()
def sensors(
    dataPath="./data",
):
    sensors = dataService.getAllSensors(dataPath)
    print(sensors)


@app.command()
def plotReceiveDelay(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensor in dataService.getAllSensors(dataPath):
            dataService.plotReceiveDelay(sensor)
    else:
        dataService.plotReceiveDelay(sensorId)


@app.command()
def plotReceiveInterval(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensor in dataService.getAllSensors(dataPath):
            dataService.plotReceiveInterval(sensor)
    else:
        dataService.plotReceiveInterval(sensorId)


@app.command()
def recoverTimestamps(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors(dataPath):
            dataService.recoverTimestamps(dataPath, sensorId)
    else:
        dataService.recoverTimestamps(dataPath, sensorId)


@app.command()
def migrate(
    dataPath="./data",
    sensorId: str = "",
):
    dataService.migrateDataToInfluxDB(dataPath, sensorId)


if __name__ == "__main__":
    app()
