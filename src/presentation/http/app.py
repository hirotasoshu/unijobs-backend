from typing import Annotated
from uuid import uuid4

import fastapi_problem_details as problem
from dishka import FromDishka
from dishka.integrations.fastapi import inject, setup_dishka
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_problem_details import ProblemResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.apply_for_vacancy import ApplyForVacancy, ApplyForVacancyDTO
from src.application.delete_application import DeleteApplication, DeleteApplicationDTO
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
from src.application.update_application import UpdateApplication, UpdateApplicationDTO
from src.application.view_models.application import ApplicationDetailViewModel
from src.application.view_models.employer import EmployerDetailViewModel
from src.application.view_models.vacancy import VacancyDetailViewModel
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
from src.domain.value_object.language import Language
from src.infra.adapters.database.models import UserModel
from src.infra.auth import create_access_token, hash_password, verify_password
from src.infra.di import get_di_container
from src.infra.identity import IdentityProvider
from src.presentation.http.dto.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from src.presentation.http.dto.application import (
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from src.presentation.http.dto.vacancy import VacancyFilters


def get_locale(accept_language: Annotated[str | None, Header()] = None) -> Language:
    if accept_language:
        return Language(accept_language)
    return Language.EN


def create_app() -> FastAPI:
    app = FastAPI()
    setup_dishka(get_di_container(), app)
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
        request: Request, exc: AnotherStudentCantChangeApplication
    ):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_403_FORBIDDEN,
            application_id=exc.application_id,
            user_id=exc.user_id,
        )

    @app.exception_handler(StudentCantChangeViewedApplication)
    async def student_cant_change_viewed_application_handler(
        request: Request, exc: StudentCantChangeViewedApplication
    ):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_400_BAD_REQUEST,
            application_id=exc.application_id,
        )

    @app.exception_handler(UserApplicationForVacancyAlreadyExists)
    async def user_application_for_vacancy_already_exists_handler(
        request: Request, exc: UserApplicationForVacancyAlreadyExists
    ):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_400_BAD_REQUEST,
            vacancy_id=exc.vacancy_id,
            user_id=exc.user_id,
        )

    @app.exception_handler(ApplicationNotFound)
    async def application_not_found_handler(request: Request, exc: ApplicationNotFound):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_404_NOT_FOUND,
            application_id=exc.application_id,
        )

    @app.exception_handler(UserApplicationForVacancyNotFound)
    async def user_application_for_vacancy_not_found_handler(
        request: Request, exc: UserApplicationForVacancyNotFound
    ):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_404_NOT_FOUND,
            vacancy_id=exc.vacancy_id,
            user_id=exc.user_id,
        )

    @app.exception_handler(EmployerNotFoundError)
    async def employer_not_found_handler(request: Request, exc: EmployerNotFoundError):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_404_NOT_FOUND,
            employer_id=exc.employer_id,
        )

    @app.exception_handler(VacancyNotFoundError)
    async def vacancy_not_found_handler(request: Request, exc: VacancyNotFoundError):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_404_NOT_FOUND,
            vacancy_id=exc.vacancy_id,
        )

    @app.exception_handler(IncorrectPagination)
    async def incorrect_pagination_handler(request: Request, exc: IncorrectPagination):
        language = Language(request.headers.get("accept-language", "en"))
        return ProblemResponse(
            type=exc.type,
            title=exc.get_title(language),
            detail=exc.get_detail_msg(language),
            status=status.HTTP_400_BAD_REQUEST,
            page=exc.page,
            page_size=exc.page_size,
        )

    @app.get("/api/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
    @inject
    async def register(
        request_body: RegisterRequest,
        session: FromDishka[AsyncSession],
    ) -> TokenResponse:
        email = request_body.email.lower()
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        if res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = UserModel(
            id=UserId(uuid4()),
            email=email,
            password_hash=hash_password(request_body.password),
            role="student",
        )
        session.add(user)
        await session.commit()
        return TokenResponse(
            access_token=create_access_token(user_id=user.id, email=user.email, role=user.role)
        )

    @app.post("/api/auth/login")
    @inject
    async def login(
        request_body: LoginRequest,
        session: FromDishka[AsyncSession],
    ) -> TokenResponse:
        email = request_body.email.lower()
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar_one_or_none()
        if user is None or not verify_password(request_body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return TokenResponse(
            access_token=create_access_token(user_id=user.id, email=user.email, role=user.role)
        )

    @app.get("/api/users/me")
    @inject
    async def get_me(
        identity_provider: FromDishka[IdentityProvider],
    ) -> CurrentUserResponse:
        user = identity_provider.current_user()
        return CurrentUserResponse(id=user.id, email=user.email, role=user.role)

    @app.get("/api/employers/{id}")
    @inject
    async def get_employer_by_id(
        id: EmployerId,
        interactor: FromDishka[GetEmployerById],
        language: Language = Depends(get_locale),
    ) -> EmployerDetailViewModel:
        return await interactor.execute(
            GetEmployerByIdDTO(employer_id=id, language=language)
        )

    @app.get("/api/vacancies")
    @inject
    async def get_vacancies_by_filters(
        query: Annotated[VacancyFilters, Query()],
        interactor: FromDishka[GetVacanciesByFilters],
        language: Language = Depends(get_locale),
    ) -> VacancyByFiltersResultDTO:
        dto = VacancyByFiltersDTO(language=language, **query.model_dump())
        return await interactor.execute(dto)

    @app.get("/api/vacancies/{id}")
    @inject
    async def get_vacancy_by_id(
        id: VacancyId,
        interactor: FromDishka[GetVacancyById],
        language: Language = Depends(get_locale),
    ) -> VacancyDetailViewModel:
        dto = VacancyByIdDTO(vacancy_id=id, language=language)
        return await interactor.execute(dto)

    @app.get("/api/users/me/applications")
    @inject
    async def get_user_applications(
        page: int,
        page_size: int,
        interactor: FromDishka[GetUserApplications],
        identity_provider: FromDishka[IdentityProvider],
        language: Language = Depends(get_locale),
    ) -> UserApplicationResultDTO:
        user_id = identity_provider.current_user().id

        dto = UserApplicationsDTO(
            user_id=user_id, page=page, page_size=page_size, language=language
        )
        return await interactor.execute(dto)

    @app.get("/api/users/me/applications/vacancies/{vacancy_id}")
    @inject
    async def get_user_application_for_vacancy(
        vacancy_id: VacancyId,
        interactor: FromDishka[GetUserApplicationForVacancy],
        identity_provider: FromDishka[IdentityProvider],
        language: Language = Depends(get_locale),
    ) -> ApplicationDetailViewModel:
        user_id = identity_provider.current_user().id

        dto = GetUserApplicationForVacancyDTO(
            user_id=user_id, vacancy_id=vacancy_id, language=language
        )
        return await interactor.execute(dto)

    @app.post("/api/users/me/applications")
    @inject
    async def create_application(
        request_body: CreateApplicationRequest,
        interactor: FromDishka[ApplyForVacancy],
        identity_provider: FromDishka[IdentityProvider],
    ) -> ApplicationId:
        user_id = identity_provider.current_user().id
        dto = ApplyForVacancyDTO(
            vacancy_id=request_body.vacancy_id,
            user_id=user_id,
            cover_letter=request_body.cover_letter,
        )
        return await interactor.execute(dto)

    @app.patch("/api/users/me/applications/{id}")
    @inject
    async def update_application(
        id: ApplicationId,
        request_body: UpdateApplicationRequest,
        interactor: FromDishka[UpdateApplication],
        identity_provider: FromDishka[IdentityProvider],
    ) -> ApplicationId:
        user_id = identity_provider.current_user().id
        dto = UpdateApplicationDTO(
            application_id=id,
            user_id=user_id,
            new_cover_letter=request_body.cover_letter,
        )
        return await interactor.execute(dto)

    @app.delete("/api/users/me/applications/{id}", status_code=status.HTTP_204_NO_CONTENT)
    @inject
    async def delete_application(
        id: ApplicationId,
        interactor: FromDishka[DeleteApplication],
        identity_provider: FromDishka[IdentityProvider],
    ) -> None:
        user_id = identity_provider.current_user().id
        dto = DeleteApplicationDTO(application_id=id, user_id=user_id)
        await interactor.execute(dto)

    return app
