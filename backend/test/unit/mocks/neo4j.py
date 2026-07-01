from unittest.mock import AsyncMock
from unittest.mock import MagicMock


def build_driver():

    session = AsyncMock()

    result = AsyncMock()

    result.data = AsyncMock(return_value=[])

    session.run = AsyncMock(return_value=result)

    driver = MagicMock()

    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)

    driver.session.return_value.__aexit__ = AsyncMock(return_value=False)

    return driver