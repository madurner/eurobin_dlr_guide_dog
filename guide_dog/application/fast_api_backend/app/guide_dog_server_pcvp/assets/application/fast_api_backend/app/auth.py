from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key = APIKeyHeader(name="x-api-key")

# TODO all information on this page needs to be private of course

map_user_to_ln_manager = {"my_secret_key": "localhost:38641", "my_secret_key_2": "localhost:38642"}


def handle_api_key(key: str = Security(api_key)):
    if key == "my_debug_key":
        # this loads the pre-set user data
        return key
    if key == "my_secret_key":
        return key
    if key == "my_secret_key_2":
        return key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")


def get_ln_manager_address_from_key(key: Annotated[str, Depends(handle_api_key)]):
    return map_user_to_ln_manager[key]
