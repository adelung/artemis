import typer
from data_service import DataService

app = typer.Typer()
dataService = DataService()


@app.command()
def sensors(
    dataPath="./data",
):
    sensorsIds = dataService.getAllSensors(dataPath)
    print(sensorsIds)


@app.command()
def collectToFile(
    dataPath="./data",
):
    dataService.collectDirectoryToFile(dataPath)


@app.command()
def plotReceiveDelay(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors(dataPath):
            dataService.plotReceiveDelay(sensorId)
    else:
        dataService.plotReceiveDelay(sensorId)


@app.command()
def plotReceiveInterval(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors(dataPath):
            dataService.plotReceiveInterval(sensorId)
    else:
        dataService.plotReceiveInterval(sensorId)


@app.command()
def recoverData(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors(dataPath):
            dataService.recoverData(dataPath, sensorId)
    else:
        dataService.recoverData(dataPath, sensorId)


@app.command()
def exportToInfluxDB(
    dataPath="./data",
    sensorId: str = "",
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors(dataPath):
            dataService.exportToInfluxDB(dataPath, sensorId)
    else:
        dataService.exportToInfluxDB(dataPath, sensorId)


if __name__ == "__main__":
    app()
