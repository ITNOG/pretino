#!/bin/env python3

"""Pretino is a web frontend for Pretix API for the ITNOG events"""

import logging

import uvicorn

from pretino.settings import Settings

LOGGER = logging.getLogger(__name__)


def main():
    """
    Main entrypoint for the application
    """
    settings = Settings()

    # App logging
    log_level = getattr(logging, settings.LOGLEVEL.name)
    logging.basicConfig()
    LOGGER.setLevel(log_level)

    # Uvicorn logging
    log_level = settings.LOGLEVEL.lower()
    reload = log_level == "debug"

    uvicorn.run(
        "pretino.webapp:create_app",
        host=str(settings.HOST),
        port=settings.PORT,
        log_level=log_level,
        reload=reload,
        factory=True,
        server_header=False,
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
