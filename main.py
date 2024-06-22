from pathlib import Path
from os import listdir, rmdir
from shutil import move
from subprocess import Popen
from sys import exit
from tempfile import NamedTemporaryFile, TemporaryDirectory
from urllib.request import urlretrieve
from zipfile import ZipFile

from requests import Response, get
from requests.exceptions import ReadTimeout

GITHUB_URL = (
    "https://api.github.com/repos/Moosems/test/releases/latest"
)

VERSION = "0.0.3"
is_frozen = False
try:
    folder = Path(__compiled__.containing_dir).resolve().parent.parent  # type: ignore # noqa: F821
    is_frozen = True
except NameError:
    folder = Path(__file__).parent

print(VERSION)


# NOTE: This should always be run in a subprocess!
def is_newest_version() -> bool:
    try:
        response: Response = get(
            GITHUB_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=3,
        )
        version: str = response.json()["tag_name"].lstrip("v")
        print(f"New version: {version}")
    except ReadTimeout:
        return False

    return True if version == VERSION else False


def download_newest_version() -> None:
    try:
        response: Response = get(
            GITHUB_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=3,
        )
    except ReadTimeout:
        return

    assets: list[dict[str, str]] = response.json()["assets"]
    print(f"Assets: {assets}")

    if not assets:
        return

    zip_path = NamedTemporaryFile(prefix="Test.app.zip")
    app_dir = TemporaryDirectory(prefix="Test")
    old_app_dir = TemporaryDirectory(prefix="OldTest")
    urlretrieve(assets[0]["browser_download_url"], zip_path.name)
    with ZipFile(zip_path.name) as zip_ref:
        zip_ref.extractall(app_dir.name)
    print("Extracted")
    print(listdir(app_dir.name))
    print(f"Moving {folder} to {old_app_dir.name}")
    move(folder, old_app_dir.name)
    print(f"Moving {app_dir.name + '/Test.app'} to /Applications/Test.app")
    move(app_dir.name + "/Test.app", "/Applications/Test.app")
    app_dir.cleanup()
    zip_path.close()
    old_app_dir.cleanup()
    Popen(
        ["chmod", "+x", "/Applications/Test.app/Contents/MacOS/Test"]
    ).wait()
    Popen(["open", "/Applications/Test.app"])
    exit(1)

if not is_newest_version() and is_frozen:
    print("Updating")
    download_newest_version()
