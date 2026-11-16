import nox
from nox.sessions import Session


@nox.session(python=("3.10", "3.11", "3.12", "3.13"))
def tests(session: Session):
    # fmt: off
    session.run(
        "uv", "export",
        "--no-hashes",
        "--all-extras",
        "--group=dev",
        "--output-file=requirements.txt",
        external=True,
    )
    # fmt: on
    session.install("-Ur", "requirements.txt")
    session.run("pytest")
