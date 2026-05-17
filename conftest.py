import pytest
from users.models import CustomUser

@pytest.fixture
def admin_user(db):
    return CustomUser.objects.create_superuser('admin', 'admin@test.com', 'password')

@pytest.fixture
def buyer_user(db):
    return CustomUser.objects.create_user('buyer', 'buyer@test.com', 'password', role='buyer')