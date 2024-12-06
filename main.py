from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter
from fhir.resources import get_fhir_model_class
from pydantic.v1 import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    debug: bool = True
    rabbitmq_url: str = "amqp://127.0.0.1:5672/"


settings = Settings()


router = RabbitRouter(settings.rabbitmq_url)


def broker():
    return router.broker


app = FastAPI()
app.include_router(router)


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/fhir/{resource_name}")
async def receive_fhir_resource(
    resource_name,
    data: dict,
    broker: Annotated[RabbitBroker, Depends(broker)],
):
    try:
        fhir_class = get_fhir_model_class(resource_name)
    except KeyError as err:
        raise HTTPException(
            status_code=404,
            detail=f"Resource {resource_name} not found",
        ) from err

    # Create a FHIR resource from the data
    # Perform a lightweight in-memory validation
    # TODO: Perform a more thorough validation to be FHIR-compliant
    fhir_resource = fhir_class(**data)
    await broker.publish(message=fhir_resource.dict(), queue=resource_name.lower())


# Handle validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    # TODO: Build a proper FHIR-compliant error response (ie. Outcome)
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )
