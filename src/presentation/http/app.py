from typing import Annotated

import fastapi_problem_details as problem
from dishka import FromDishka
from dishka.integrations.fastapi import inject, setup_dishka
from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_problem_details import ProblemResponse

from src.application.get_employer_by_id import GetEmployerById, GetEmployerByIdDTO
from src.application.get_vacancies_by_filters import (
    GetVacanciesByFilters,
    VacancyByFiltersDTO,
    VacancyByFiltersResultDTO,
)
from src.application.get_vacancy_by_id import GetVacancyById, VacancyByIdDTO
from src.application.view_models.employer import EmployerDetailViewModel
from src.application.view_models.vacancy import VacancyDetailViewModel
from src.domain.exception.employer import EmployerNotFoundError
from src.domain.exception.pagination import IncorrectPagination
from src.domain.exception.vacancy import VacancyNotFoundError
from src.domain.value_object.ids import EmployerId, VacancyId
from src.infra.di import get_di_container
from src.presentation.http.dto.vacancy import VacancyFilters


def create_app() -> FastAPI:
    app = FastAPI()
    _ = problem.init_app(app)
    setup_dishka(get_di_container(), app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(EmployerNotFoundError)
    async def employer_not_found_handler(_: Request, exc: EmployerNotFoundError):
        return ProblemResponse(
            type="EmployerNotFound",
            title="Employer not found",
            detail=str(exc),
            status=status.HTTP_404_NOT_FOUND,
            employer_id=exc.employer_id,
        )

    @app.exception_handler(VacancyNotFoundError)
    async def vacancy_not_found_handler(_: Request, exc: VacancyNotFoundError):
        return ProblemResponse(
            type="VacancyNotFound",
            title="Vacancy not found",
            detail=str(exc),
            status=status.HTTP_404_NOT_FOUND,
            vacancy_id=exc.vacancy_id,
        )

    @app.exception_handler(IncorrectPagination)
    async def incorrect_pagination_handler(_: Request, exc: IncorrectPagination):
        return ProblemResponse(
            type="IncorrectPagination",
            title="Incorrect pagination params",
            detail=str(exc),
            status=status.HTTP_400_BAD_REQUEST,
            page=exc.page,
            page_size=exc.page_size,
        )

    @app.get("/employers/{id}")
    @inject
    async def get_employer_by_id(
        id: EmployerId, interactor: FromDishka[GetEmployerById]
    ) -> EmployerDetailViewModel:
        return await interactor.execute(GetEmployerByIdDTO(employer_id=id))

    @app.get("/vacancies")
    @inject
    async def get_vacancies_by_filters(
        query: Annotated[VacancyFilters, Query()],
        interactor: FromDishka[GetVacanciesByFilters],
    ) -> VacancyByFiltersResultDTO:
        dto = VacancyByFiltersDTO(**query.model_dump())
        return await interactor.execute(dto)

    @app.get("/vacancies/{id}")
    @inject
    async def get_vacancy_by_id(
        id: VacancyId, interactor: FromDishka[GetVacancyById]
    ) -> VacancyDetailViewModel:
        dto = VacancyByIdDTO(vacancy_id=id)
        return await interactor.execute(dto)

    return app
