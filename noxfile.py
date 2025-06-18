import nox
from nox.sessions import Session


@nox.session(python=("3.10", "3.11", "3.12", "3.13"))
def tests(session: Session):
    # fmt: off
    session.run(
        "poetry", "export",
        "--with=dev",
        "--output=requirements.txt",
        "--extras=toml",
        "--extras=yaml",
        "--extras=arrow",
        "--extras=msgpack",
        "--extras=pint",
        external=True,
    )
    # fmt: on
    session.install("-Ur", "requirements.txt")
    session.run("pytest")
