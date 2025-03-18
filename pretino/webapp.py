"""USGI webapp"""

import logging
from collections.abc import AsyncIterable
from typing import Optional, TypedDict

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

from pretino.settings import Settings

logger = logging.getLogger(__name__)


class Attendee(TypedDict):
    """
    Attendee data structure
    """

    name: str
    company: str
    asn: str


class Order(TypedDict):
    """
    Order data structure
    """

    name: str
    company: str
    asn: str
    job_title: str
    email: str
    order_id: str
    bio_url: str
    tshirt_size: str


def authorize_api_key(settings: Settings, api_key: str) -> tuple[bool, bool]:
    """
    Authorizes and API key

    Arguments:
    ----------
    settings: Settings
        App settings object
    api_key: str
        API key to authorize

    Returns:
    --------
    tuple[bool, bool]: API key is authorized, API key is privileged
    """
    for api_key_object in settings.API_KEYS:
        if api_key_object.key == api_key:
            return True, api_key_object.privileged

    return False, False


async def get_orders_from_pretix(
    organizer: str, event_name: str, api_token: str, question_mapping: dict[str, str]
) -> AsyncIterable[Order]:
    """
    Downloads order data from a Pretix.

    Arguments:
    ----------
    organizer: str
        Pretix organizer name
    event_name: str
        Pretix name of the event
    api_token: str
        Pretix API token

    Returns:
    --------
    Generator[TypedDict]: Yield Orders
    """

    base_url = f"https://pretix.eu/api/v1/organizers/{organizer}/events/{event_name}/orders/"
    headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}

    # Reverse mapping for faster lookups
    question_mapping = {value: key for key, value in question_mapping.items()}

    url = f"{base_url}?require_approval=true"
    while url:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()

                for result in data["results"]:
                    for position in result["positions"]:
                        # Import answers to "questions"
                        order = {
                            question_mapping[answer["question_identifier"]]: answer["answer"]
                            for answer in position["answers"]
                            if answer["question_identifier"] in question_mapping
                        }

                        # Import static fields
                        order["name"] = position["attendee_name"]
                        order["email"] = position["attendee_email"]
                        order["order_id"] = position["order"]

                        yield Order(**order)

            url = data["next"]
        except httpx.RequestError as error:
            logger.error("Error during API request: %s", error)
            break


def create_app(settings: Optional[Settings] = False) -> FastAPI:
    """
    Webapp factory

    Arguments:
    ---------
    settings: Optional[Settings] = False
        Application settings

    Returns:
    --------
    FasAPI: Application instance
    """
    settings = settings or Settings()
    webapp = FastAPI(
        title="Pretino",
        summary="Pretino is a web frontend for Pretix API for the ITNOG events",
    )

    api_key_header_scheme = APIKeyHeader(name="x-pretino-key")

    @webapp.get("/attendees", tags=["Attendees"])
    async def get_attendees(api_key: str = Depends(api_key_header_scheme)) -> list[Attendee]:
        authorized, _ = authorize_api_key(settings, api_key)
        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        return [
            Attendee(company=order["company"], name=order["name"], asn=order["asn"])
            async for order in get_orders_from_pretix(  # NOSONAR
                settings.ORGANIZER,
                settings.EVENT_NAME,
                settings.API_TOKEN,
                settings.QUESTION_MAPPING.model_dump(),
            )
        ]

    @webapp.get("/orders", tags=["Orders"])
    async def get_orders(api_key: str = Depends(api_key_header_scheme)) -> list[Order]:
        authorized, privileged = authorize_api_key(settings, api_key)
        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        if not privileged:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unprivileged API key",
            )

        return list(
            get_orders_from_pretix(
                settings.ORGANIZER,
                settings.EVENT_NAME,
                settings.API_TOKEN,
                settings.QUESTION_MAPPING.model_dump(),
            )
        )

    return webapp
