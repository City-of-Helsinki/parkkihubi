import io

from django.core import management


def call_mgmt_cmd_with_output(command_cls, *args, **kwargs):
    assert issubclass(command_cls, management.BaseCommand)
    stdout = io.StringIO()
    stderr = io.StringIO()
    cmd = command_cls(stdout=stdout, stderr=stderr)
    assert isinstance(cmd, management.BaseCommand)
    result = management.call_command(cmd, *args, **kwargs)
    return (result, stdout.getvalue(), stderr.getvalue())
