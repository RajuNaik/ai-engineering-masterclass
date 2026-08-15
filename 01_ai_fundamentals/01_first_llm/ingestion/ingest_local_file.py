from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


# ============================================================
# Configuration
# ============================================================

STORAGE_ACCOUNT_NAME = "aiengrag"
FILE_SYSTEM_NAME = "rag-raw"
TARGET_DIRECTORY = "files"


# ============================================================
# ADLS connection
# ============================================================

account_url = f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net"
credential = DefaultAzureCredential()

service_client = DataLakeServiceClient(
    account_url=account_url,
    credential=credential,
)


# ============================================================
# Upload function
# ============================================================

def upload_file_to_adls(local_file_path: str) -> None:
    local_file = Path(local_file_path)

    if not local_file.exists():
        raise FileNotFoundError(f"Local file not found: {local_file}")

    if not local_file.is_file():
        raise ValueError(f"Path is not a file: {local_file}")

    file_system_client = service_client.get_file_system_client(FILE_SYSTEM_NAME)

    directory_client = file_system_client.get_directory_client(TARGET_DIRECTORY)

    # Directory creation is intentionally idempotent for this first test.
    try:
        directory_client.create_directory()
    except Exception as exc:
        # If the directory already exists, continue to the upload.
        if "already exists" not in str(exc).lower():
            raise

    file_client = directory_client.get_file_client(local_file.name)

    with local_file.open("rb") as data:
        file_client.upload_data(data, overwrite=True)

    print("Upload successful!")
    print(f"Source      : {local_file.resolve()}")
    print(
        "Destination : "
        f"{FILE_SYSTEM_NAME}/{TARGET_DIRECTORY}/{local_file.name}"
    )


if __name__ == "__main__":
    # Test document committed in this repository.
    test_file = Path(__file__).resolve().parent.parent / "rag_test_policy.txt"
    upload_file_to_adls(str(test_file))
