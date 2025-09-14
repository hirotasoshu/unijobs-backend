import fastapi_problem_details as problem
from dishka import FromDishka
from dishka.integrations.fastapi import inject, setup_dishka
from fastapi import FastAPI, Request, status
from fastapi_problem_details import ProblemResponse

from src.application.get_employer_by_id import GetEmployerById, GetEmployerByIdDTO
from src.application.view_models.employer import EmployerDetailViewModel
from src.domain.exception.employer import EmployerNotFoundError
from src.domain.value_object.ids import EmployerId
from src.infra.di import get_di_container


def create_app() -> FastAPI:
    app = FastAPI()
    _ = problem.init_app(app)
    setup_dishka(get_di_container(), app)

    @app.exception_handler(EmployerNotFoundError)
    async def employer_not_found_handler(_: Request, exc: EmployerNotFoundError):
        return ProblemResponse(
            type="EmployerNotFound",
            title="Employer not found",
            detail=str(exc),
            status=status.HTTP_404_NOT_FOUND,
            employer_id=exc.employer_id,
        )

    @app.get("/employers/{id}")
    @inject
    async def get_employer_by_id(
        id: EmployerId, interactor: FromDishka[GetEmployerById]
    ) -> EmployerDetailViewModel:
        return await interactor.execute(GetEmployerByIdDTO(employer_id=id))

    return app
