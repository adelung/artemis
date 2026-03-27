import typer
from typing import Annotated, Callable
from data_service import DataService

app = typer.Typer()
dataService = DataService("./data", "./data")


@app.command()
def sensors():
    sensorsIds = dataService.getAllSensors()
    print(sensorsIds)


@app.command()
def collectToFile(
    sensorId: str = "",
    iso: Annotated[bool, typer.Option("--iso")] = False,
):
    runAllSensors(
        sensorId,
        lambda id: dataService.collectDirectoryToFile(id, iso),
    )


@app.command()
def plotReceiveDelay(
    sensorId: str = "",
):
    runAllSensors(
        sensorId,
        lambda id: dataService.plotReceiveDelay(id),
    )


@app.command()
def plotReceiveInterval(
    sensorId: str = "",
):
    runAllSensors(
        sensorId,
        lambda id: dataService.plotReceiveInterval(id),
    )


@app.command()
def recoverData(
    sensorId: str = "",
):
    runAllSensors(
        sensorId,
        lambda id: dataService.recoverData(id),
    )


@app.command()
def exportToInfluxDB(
    sensorId: str = "",
):
    runAllSensors(
        sensorId,
        lambda id: dataService.exportToInfluxDB(id),
    )


def runAllSensors(
    sensorId: str | None,
    task: Callable[[str], None],
):
    if sensorId == "":
        for sensorId in dataService.getAllSensors():
            task(sensorId)
    else:
        task(sensorId)


if __name__ == "__main__":
    app()
