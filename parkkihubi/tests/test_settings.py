import contextlib
import os
from importlib import reload
from unittest.mock import ANY, patch


def test_sentry_init():
    env = {
        "SENTRY_DSN": "http://localhost/dummy-sentry-dsn",
        "SENTRY_ENVIRONMENT": "just-test",
    }
    with override_env(**env):
        with patch("sentry_sdk.init") as mock_sentry_init:
            from parkkihubi import settings

            reload(settings)

            assert settings.SENTRY_DSN == "http://localhost/dummy-sentry-dsn"
            mock_sentry_init.assert_called_with(
                dsn="http://localhost/dummy-sentry-dsn",
                environment="just-test",
                send_default_pii=True,
                attach_stacktrace=True,
                integrations=ANY,
            )


def test_sentry_init_is_skipped_without_dsn():
    with override_env(SENTRY_DSN=""):
        with patch("sentry_sdk.init") as mock_sentry_init:
            from parkkihubi import settings

            reload(settings)

            assert settings.SENTRY_DSN == ""
            mock_sentry_init.assert_not_called()


@contextlib.contextmanager
def override_env(**env_vars):
    original_env = {key: os.environ.get(key) for key in env_vars}
    os.environ.update(env_vars)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value
                os.environ[key] = value
