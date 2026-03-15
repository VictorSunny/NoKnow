import pytest

from src.tests.conftest import test_client


class TestUtilities:
    def test_hash_password_and_verify_password(test_client):
        raw_password = "This!s3password"
