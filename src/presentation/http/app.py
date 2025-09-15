from typing import Annotated, Any
from uuid import UUID

import fastapi_problem_details as problem
from dishka import FromDishka
from dishka.integrations.fastapi import inject, setup_dishka
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import setup_keycloak_middleware
from fastapi_problem_details import ProblemResponse

from src.application.apply_for_vacancy import ApplyForVacancy, ApplyForVacancyDTO
from src.application.update_application import UpdateApplication, UpdateApplicationDTO
from src.application.get_employer_by_id import GetEmployerById, GetEmployerByIdDTO
from src.application.get_user_application_for_vacancy import (
    GetUserApplicationForVacancy,
    GetUserApplicationForVacancyDTO,
)
from src.application.get_user_applications import (
    GetUserApplications,
    UserApplicationResultDTO,
    UserApplicationsDTO,
)
from src.application.get_vacancies_by_filters import (
    GetVacanciesByFilters,
    VacancyByFiltersDTO,
    VacancyByFiltersResultDTO,
)
from src.application.get_vacancy_by_id import GetVacancyById, VacancyByIdDTO
from src.application.view_models.employer import EmployerDetailViewModel
from src.application.view_models.vacancy import VacancyDetailViewModel
from src.application.view_models.application import ApplicationDetailViewModel
from src.domain.exception.application import (
    AnotherStudentCantChangeApplication,
    ApplicationNotFound,
    StudentCantChangeViewedApplication,
    UserApplicationForVacancyAlreadyExists,
    UserApplicationForVacancyNotFound,
)
from src.domain.exception.employer import EmployerNotFoundError
from src.domain.exception.pagination import IncorrectPagination
from src.domain.exception.vacancy import VacancyNotFoundError
from src.domain.value_object.ids import ApplicationId, EmployerId, UserId, VacancyId
from src.infra.di import get_di_container
from src.infra.idp import idp_config
from src.presentation.http.dto.application import (
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from src.presentation.http.dto.vacancy import VacancyFilters


async def _get_user(userinfo: dict[str, Any]) -> dict[str, UserId]:
    return {"user_id": UserId(UUID(userinfo["sub"]))}


def create_app() -> FastAPI:
    app = FastAPI()
    setup_dishka(get_di_container(), app)
    setup_keycloak_middleware(
        app,
        keycloak_configuration=idp_config,
        exclude_patterns=["/docs", "/openapi.json", "/vacancies", "/employers"],
        user_mapper=_get_user,
    )
    _ = problem.init_app(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AnotherStudentCantChangeApplication)
    async def another_student_cant_change_application_handler(
        _: Request, exc: AnotherStudentCantChangeApplication
    ):
        return ProblemResponse(
            type="AnotherStudentCantChangeApplication",
            title="Student can't change other person's application",
            detail=str(exc),
            status=status.HTTP_403_FORBIDDEN,
            application_id=exc.application_id,
            user_id=exc.user_id,
        )

    @app.exception_handler(StudentCantChangeViewedApplication)
    async def student_cant_change_viewed_application_handler(
        _: Request, exc: StudentCantChangeViewedApplication
    ):
        return ProblemResponse(
            type="CantChangeViewedApplication",
            title="Student can't change viewed application",
            detail=str(exc),
            status=status.HTTP_400_BAD_REQUEST,
            application_id=exc.application_id,
        )

    @app.exception_handler(UserApplicationForVacancyAlreadyExists)
    async def user_application_for_vacancy_already_exists_handler(
        _: Request, exc: UserApplicationForVacancyAlreadyExists
    ):
        return ProblemResponse(
            type="ApplicationAlreadyExists",
            title="application already exists",
            detail=str(exc),
            status=status.HTTP_400_BAD_REQUEST,
            vacancy_id=exc.vacancy_id,
            user_id=exc.user_id,
        )

    @app.exception_handler(ApplicationNotFound)
    async def application_not_found_handler(_: Request, exc: ApplicationNotFound):
        return ProblemResponse(
            type="ApplicationNotFound",
            title="application not found",
            detail=str(exc),
            status=status.HTTP_404_NOT_FOUND,
            application_id=exc.application_id,
        )

    @app.exception_handler(UserApplicationForVacancyNotFound)
    async def user_application_for_vacancy_not_found_handler(
        _: Request, exc: UserApplicationForVacancyNotFound
    ):
        return ProblemResponse(
            type="ApplicationNotFound",
            title="application not found",
            detail=str(exc),
            status=status.HTTP_404_NOT_FOUND,
            vacancy_id=exc.vacancy_id,
            user_id=exc.user_id,
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

    @app.get("/users/me/applications")
    @inject
    async def get_user_applications(
        page: int,
        page_size: int,
        request: Request,
        interactor: FromDishka[GetUserApplications],
    ) -> UserApplicationResultDTO:
        if "user" not in request.scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to retrieve user from request",
            )
        user_id = request.scope["user"]["user_id"]

        dto = UserApplicationsDTO(user_id=user_id, page=page, page_size=page_size)
        return await interactor.execute(dto)

    @app.get("/users/me/applications/vacancies/{vacancy_id}")
    @inject
    async def get_user_application_for_vacancy(
        vacancy_id: VacancyId,
        request: Request,
        interactor: FromDishka[GetUserApplicationForVacancy],
    ) -> ApplicationDetailViewModel:
        if "user" not in request.scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to retrieve user from request",
            )
        user_id = request.scope["user"]["user_id"]

        dto = GetUserApplicationForVacancyDTO(user_id=user_id, vacancy_id=vacancy_id)
        return await interactor.execute(dto)

    @app.post("/users/me/applications")
    @inject
    async def create_application(
        request_body: CreateApplicationRequest,
        request: Request,
        interactor: FromDishka[ApplyForVacancy],
    ) -> ApplicationId:
        if "user" not in request.scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to retrieve user from request",
            )
        user_id = request.scope["user"]["user_id"]
        dto = ApplyForVacancyDTO(
            vacancy_id=request_body.vacancy_id,
            user_id=user_id,
            cover_letter=request_body.cover_letter,
        )
        return await interactor.execute(dto)

    @app.patch("/users/me/applications/{id}")
    @inject
    async def update_application(
        id: ApplicationId,
        request_body: UpdateApplicationRequest,
        request: Request,
        interactor: FromDishka[UpdateApplication],
    ) -> ApplicationId:
        if "user" not in request.scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to retrieve user from request",
            )
        user_id = request.scope["user"]["user_id"]
        dto = UpdateApplicationDTO(
            application_id=id,
            user_id=user_id,
            new_cover_letter=request_body.cover_letter,
        )
        return await interactor.execute(dto)

    return app
