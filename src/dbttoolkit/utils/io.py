import json
from pathlib import Path
from typing import Mapping

from google.cloud import storage

from dbttoolkit.utils.logger import get_logger

logger = get_logger()


def persist(content: str, output_folder: Path, filename: str, *, bucket_name: str = None):
    """
    Writes either to a local file or remotely to a bucket if "bucket_name" is provided

    :param content: the string to be written
    :param output_folder: the path to the folder
    :param filename: the name of the file
    :param bucket_name: the name of the bucket
    :return: None
    """
    if bucket_name:
        write_to_bucket(content, bucket_name, output_folder, filename)
    else:
        write_to_file(content, output_folder, filename)


def write_to_bucket(content: str, bucket_name: str, output_folder: Path, filename: str) -> None:
    """
    Uploads files to a GCS bucket

    :param content: the string to be written
    :param bucket_name: the name of the bucket
    :param output_folder: the relative path in the bucket
    :param filename: the name of the file
    :return:  None
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    file_path = Path(output_folder, filename)
    blob = bucket.blob(str(file_path))

    logger.info(f"Uploading to GCS: {bucket_name}, {file_path}")

    blob.upload_from_string(content)


def write_to_file(content: str, output_folder: Path, filename: str) -> None:
    """
    Writes a string to a file.
    Takes care of creating the folder if necessary

    :param content: the string to be written
    :param output_folder: the path to the folder
    :param filename: the name of the file
    :return: None
    """
    Path.mkdir(output_folder, parents=True, exist_ok=True)

    logger.info(f"Writing to file: {output_folder / filename}")

    with open(output_folder / filename, "w") as file:
        file.write(content)


def load_json_file(path) -> dict:
    with open(path) as file:
        manifest = json.load(file)

    return manifest


def write_json_file(json_object: Mapping, output_path: Path) -> None:
    with open(output_path, "w") as file:
        json.dump(json_object, file, indent=4)
