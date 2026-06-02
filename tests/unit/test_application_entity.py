from uuid import uuid4

import pytest

from src.domain.entity.application import Application
from src.domain.exception.application import StudentCantChangeViewedApplication
from src.domain.value_object.application_status import ApplicationStatus


pytestmark = pytest.mark.unit


def test_application_rejects_changes_after_review_started():
    application = Application(
        user_id=uuid4(),
        vacancy_id=uuid4(),
        cover_letter="Initial cover letter",
        status=ApplicationStatus.REVIEW,
    )

    with pytest.raises(StudentCantChangeViewedApplication):
        application.ensure_can_be_changed()


def test_application_allows_changes_while_pending():
    application = Application(
        user_id=uuid4(),
        vacancy_id=uuid4(),
        cover_letter="Initial cover letter",
        status=ApplicationStatus.PENDING,
    )

    application.ensure_can_be_changed()
