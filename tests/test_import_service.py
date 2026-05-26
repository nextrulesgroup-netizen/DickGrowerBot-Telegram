import pytest
from types import SimpleNamespace

from app.repositories.import_log import ImportLogRepository
from app.repositories.user import UserRepository
from app.services.importer import ImportService


@pytest.mark.asyncio
async def test_import_csv_and_json(session):
    settings = SimpleNamespace()
    user_repo = UserRepository(session)
    import_log_repo = ImportLogRepository(session)
    importer = ImportService(user_repo, import_log_repo)

    csv_data = "telegram_id,username,full_name,language\n123,tester,Tester,en\n"
    count_csv = await importer.import_csv("test_csv", csv_data)
    assert count_csv == 1

    json_data = "[{\"telegram_id\": 124, \"username\": \"tester2\", \"full_name\": \"Tester 2\", \"language\": \"ru\"}]"
    count_json = await importer.import_json("test_json", json_data)
    assert count_json == 1

    logs = await import_log_repo.list_recent()
    assert any(log.status == "completed" for log in logs)
