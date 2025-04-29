import yaml


def read_yaml(file_path: str) -> dict:
    """
    Read a YAML file.
    :param file_path: The file path.
    :return: The YAML content.
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

