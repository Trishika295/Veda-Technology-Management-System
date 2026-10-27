import os
from typing import Optional, Dict, Any, List
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api")


class APIError(Exception):
    """Custom exception for API errors with status code and detail."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
        stream: bool = False
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(token)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=timeout,
                stream=stream
            )
        except requests.exceptions.ConnectionError:
            raise APIError("Cannot connect to backend server. Please verify FastAPI is running at " + self.base_url)
        except requests.exceptions.Timeout:
            raise APIError("Backend request timed out. Please try again.")
        except Exception as e:
            raise APIError(f"Unexpected connection error: {str(e)}")

        if not response.ok:
            error_msg = f"HTTP {response.status_code}"
            try:
                data = response.json()
                if isinstance(data, dict) and "detail" in data:
                    detail = data["detail"]
                    if isinstance(detail, list):
                        # Pydantic validation errors
                        error_msg = "; ".join([f"{err.get('loc', [''])[ -1]}: {err.get('msg', '')}" for err in detail])
                    else:
                        error_msg = str(detail)
                elif isinstance(data, str):
                    error_msg = data
            except Exception:
                error_msg = response.text or error_msg
            raise APIError(error_msg, status_code=response.status_code)

        if response.status_code == 204:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    # --- Health ---
    def check_health(self) -> Dict[str, Any]:
        return self._request("GET", "/health")

    # --- Auth ---
    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self._request("POST", "/auth/login", json_data={"email": email, "password": password})

    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("POST", "/auth/register", json_data=user_data)

    def get_me(self, token: str) -> Dict[str, Any]:
        return self._request("GET", "/auth/me", token=token)

    # --- Dashboard ---
    def get_dashboard(self, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", "/dashboard", token=token)

    # --- Technology Programs ---
    def get_programs(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        return self._request("GET", "/programs", token=token, params=params)

    def get_program(self, program_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/programs/{program_id}", token=token)

    def create_program(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/programs", token=token, json_data=data)

    def update_program(self, program_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/programs/{program_id}", token=token, json_data=data)

    def delete_program(self, program_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/programs/{program_id}", token=token)

    # --- Digital Services ---
    def get_services(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        return self._request("GET", "/services", token=token, params=params)

    def get_service(self, service_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/services/{service_id}", token=token)

    def create_service(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/services", token=token, json_data=data)

    def update_service(self, service_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/services/{service_id}", token=token, json_data=data)

    def delete_service(self, service_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/services/{service_id}", token=token)

    # --- Training & Internships ---
    def get_training_programs(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        program_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if program_type and program_type != "All":
            params["program_type"] = program_type
        if status and status != "All":
            params["status"] = status
        return self._request("GET", "/training-programs", token=token, params=params)

    def get_training_program(self, program_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/training-programs/{program_id}", token=token)

    def create_training_program(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/training-programs", token=token, json_data=data)

    def update_training_program(self, program_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/training-programs/{program_id}", token=token, json_data=data)

    def delete_training_program(self, program_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/training-programs/{program_id}", token=token)

    # --- Customers ---
    def get_customers(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        return self._request("GET", "/customers", token=token, params=params)

    def get_customer(self, customer_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/customers/{customer_id}", token=token)

    def create_customer(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/customers", token=token, json_data=data)

    def update_customer(self, customer_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/customers/{customer_id}", token=token, json_data=data)

    def delete_customer(self, customer_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/customers/{customer_id}", token=token)

    # --- Customer Inquiries ---
    def get_inquiries(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        if priority and priority != "All":
            params["priority"] = priority
        return self._request("GET", "/inquiries", token=token, params=params)

    def get_inquiry(self, inquiry_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/inquiries/{inquiry_id}", token=token)

    def create_inquiry(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/inquiries", token=token, json_data=data)

    def update_inquiry(self, inquiry_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/inquiries/{inquiry_id}", token=token, json_data=data)

    def delete_inquiry(self, inquiry_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/inquiries/{inquiry_id}", token=token)

    # --- Service Requests ---
    def get_service_requests(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if search:
            params["search"] = search
        if category and category != "All":
            params["category"] = category
        if status and status != "All":
            params["status"] = status
        if priority and priority != "All":
            params["priority"] = priority
        return self._request("GET", "/service-requests", token=token, params=params)

    def get_service_request(self, request_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", f"/service-requests/{request_id}", token=token)

    def create_service_request(self, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("POST", "/service-requests", token=token, json_data=data)

    def update_service_request(self, request_id: str, data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("PUT", f"/service-requests/{request_id}", token=token, json_data=data)

    def delete_service_request(self, request_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("DELETE", f"/service-requests/{request_id}", token=token)

    # --- Reports & CSV Export ---
    def get_reports(self, token: Optional[str] = None) -> Dict[str, Any]:
        return self._request("GET", "/reports", token=token)

    def get_csv_export(self, module: str, token: Optional[str] = None) -> str:
        url = f"{self.base_url}/reports/export-csv"
        headers = self._get_headers(token)
        try:
            resp = requests.get(url, headers=headers, params={"module": module}, timeout=20)
            if not resp.ok:
                raise APIError(f"Failed to export CSV: {resp.status_code}")
            return resp.text
        except Exception as e:
            raise APIError(f"Failed to download CSV: {str(e)}")

    # --- Activity History ---
    def get_activity(
        self,
        token: Optional[str] = None,
        search: Optional[str] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        params = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        if module and module != "All":
            params["module"] = module
        if action and action != "All":
            params["action"] = action
        return self._request("GET", "/activity", token=token, params=params)


# Singleton instance
api = APIClient()
