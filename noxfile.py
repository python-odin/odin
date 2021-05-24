import nox
from nox.sessions import Session


@nox.session(python=("2.7", "3.8"), reuse_venv=True)
def tests(session: Session):
    # fmt: off
    session.run(
        "poetry", "export",
        "--dev",
        "-o", "requirements.txt",
        "-E", "toml",
        "-E", "yaml",
        "-E", "arrow",
        "-E", "msgpack",
        external=True,
    )
    # fmt: on
    session.install("-r", "requirements.txt")
    session.run("pytest")
