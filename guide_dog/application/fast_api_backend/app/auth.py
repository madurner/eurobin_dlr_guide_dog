from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key = APIKeyHeader(name="x-api-key")

def handle_api_key(key: str = Security(api_key)):
    if key == "socrob_tests": # TODO all information on this page will be private in actual deployment
        return key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
