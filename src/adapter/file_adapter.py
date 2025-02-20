from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
from src.utils.http_client import HttpClient
from src.adapter.exceptions import FileManagerAdapterException
from src.models.response import FileResponse

@dataclass
class FileRequest:
    """Data class for file request parameters."""
    bucket_id: str
    directory: Optional[str] = None
    file_path: Optional[str] = None
    file: Optional[Any] = None

class FileAdapter:
    """Adapter to interact with the file management microservice paths."""

    def __init__(self, base_url: str, http_client: HttpClient) -> None:
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if not isinstance(http_client, HttpClient):
            raise ValueError("http_client must be an instance of HttpClient")
            
        self._base_url: str = base_url.rstrip('/')
        self._http_client: HttpClient = http_client
        self._file_endpoint: str = f"{self._base_url}/file"

    def save_file(self, request: FileRequest) -> Dict[str, Any]:
        """Saves a file to the microservice."""
        self._validate_save_request(request)
        return self._post(
            self._file_endpoint,
            self._prepare_file_data(request)
        )

    def get_file(self, request: FileRequest) -> FileResponse:
        """Gets a file from the microservice.
        
        Returns:
            FileResponse containing either file data or JSON response
        """
        self._validate_get_request(request)
        url = self._build_url_with_params(
            self._file_endpoint,
            bucket_id=request.bucket_id,
            file_path=request.file_path
        )
        return self._get(url)

    def update_file(self, request: FileRequest) -> Dict[str, Any]:
        """Updates a file in the microservice."""
        self._validate_save_request(request)
        return self._put(
            self._file_endpoint,
            self._prepare_file_data(request)
        )

    def delete_file(self, request: FileRequest) -> Dict[str, Any]:
        """Deletes a file from the microservice."""
        self._validate_get_request(request)
        url = self._build_url_with_params(
            self._file_endpoint,
            bucket_id=request.bucket_id,
            file_path=request.file_path
        )
        return self._delete(url)

    def _prepare_file_data(self, request: FileRequest) -> Dict[str, Any]:
        """Prepares file data for request."""
        data = {"bucket_id": request.bucket_id}
        if request.directory:
            data["directory"] = request.directory
        if request.file:
            data["file"] = request.file
        return data

    def _build_url_with_params(self, base_url: str, **params: str) -> str:
        """Builds URL with query parameters."""
        query_params = "&".join(f"{k}={v}" for k, v in params.items() if v)
        return f"{base_url}?{query_params}"

    def _validate_save_request(self, request: FileRequest) -> None:
        """Validates save/update request parameters."""
        if not request.bucket_id or not request.directory or not request.file:
            raise FileManagerAdapterException(
                "bucket_id, directory and file are required for save/update operations"
            )

    def _validate_get_request(self, request: FileRequest) -> None:
        """Validates get/delete request parameters."""
        if not request.bucket_id or not request.file_path:
            raise FileManagerAdapterException(
                "bucket_id and file_path are required for get/delete operations"
            )

    def _post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a POST request using HTTP client."""
        files = {'file': data.pop('file')} if 'file' in data else None
        return self._http_client.post_file(url, data=data, files=files)

    def _get(self, url: str) -> FileResponse:
        """Performs a GET request using HTTP client."""
        return self._http_client.get_file(url)

    def _put(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a PUT request using HTTP client."""
        files = {'file': data.pop('file')} if 'file' in data else None
        return self._http_client.update_file(url, data=data, files=files)

    def _delete(self, url: str) -> Dict[str, Any]:
        """Performs a DELETE request using HTTP client."""
        return self._http_client.delete_file(url)
