from jinja2 import Environment, PackageLoader, select_autoescape
from typing import NamedTuple, List, Optional
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)


class ExecutionEnvironment(NamedTuple):
    """Class to represent an execution environment."""

    name: str
    tag: str


def get_folder_names(directory: str) -> List[str]:
    """Return a list of folder names in the given directory."""
    return [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]


def get_headers() -> dict:
    """Return the headers for the requests.get call."""
    token = os.getenv("GHCR_TOKEN")
    if not token:
        raise ValueError("Missing environment variable: GHCR_TOKEN")
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }


def get_latest_image_tag(name: str) -> Optional[str]:
    """Return the latest image tag for the given name."""
    try:
        r = requests.get(
            f"https://api.github.com/users/nickarellano/packages/container/ee-{name}/versions",
            headers=get_headers(),
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
        raise
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise
    else:
        data = r.json()
        for image in data:
            if image["metadata"]["container"]["tags"]:
                return image["metadata"]["container"]["tags"][0]
        return None


def main() -> None:
    """Main function to get folder names and write to README."""
    environments = get_folder_names("environments")
    environments = [
        ExecutionEnvironment(name, get_latest_image_tag(name)) for name in environments
    ]

    template = env.get_template("README.md.j2")
    with open("README.md", "w") as f:
        f.write(template.render(environments=environments))


env = Environment(loader=PackageLoader("render-readme"), autoescape=select_autoescape())

if __name__ == "__main__":
    main()
