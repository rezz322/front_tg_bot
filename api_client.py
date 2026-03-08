from api_admin import AdminAPI
from api_user import UserAPI

class BackendAPI(AdminAPI, UserAPI):
    """
    Aggregator class that combines Admin and User API functionalities.
    Maintained for backward compatibility.
    """
    pass

backend_api = BackendAPI()
