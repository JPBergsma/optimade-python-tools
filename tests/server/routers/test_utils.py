"""Tests specifically for optimade.servers.routers.utils."""
from typing import Mapping, Optional, Tuple, Union
from unittest import mock

from requests.exceptions import ConnectionError

import pytest


def mocked_providers_list_response(
    url: Union[str, bytes] = "",
    param: Optional[Union[Mapping[str, str], Tuple[str, str]]] = None,
    **kwargs,
):
    """This function will be used to mock requests.get

    It will _always_ return a successful response, returning the submodule's provider.json.

    NOTE: This function is loosely inspired by the stackoverflow response here:
        https://stackoverflow.com/questions/15753390/how-can-i-mock-requests-and-the-response
    """
    try:
        from optimade.server.data import providers
    except ImportError:
        pytest.fail(
            "Cannot import providers from optimade.server.data, "
            "please initialize the `providers` submodule!"
        )

    class MockResponse:
        def __init__(self, data: Union[list, dict], status_code: int):
            self.data = data
            self.status_code = status_code

        def json(self) -> Union[list, dict]:
            return self.data

    return MockResponse(providers, 200)


def test_get_providers():
    """Make sure valid responses are handled as expected."""
    try:
        from optimade.server.data import providers
    except ImportError:
        pytest.fail(
            "Cannot import providers from optimade.server.data, "
            "please initialize the `providers` submodule!"
        )

    from optimade.server.routers.utils import get_providers, mongo_id_for_database

    side_effects = [
        mocked_providers_list_response,
        ConnectionError,
    ]

    for side_effect in side_effects:
        with mock.patch("requests.get", side_effect=side_effect):
            providers_list = [
                _ for _ in providers.get("data", []) if _["id"] != "exmpl"
            ]
            for provider in providers_list:
                provider.update(
                    {
                        "_id": {
                            "$oid": mongo_id_for_database(
                                provider["id"], provider["type"]
                            )
                        }
                    }
                )
            assert get_providers() == providers_list


def test_get_providers_warning(caplog, top_dir):
    """Make sure a warning is logged as a last resort."""
    import copy
    from optimade.server.routers.utils import get_providers, PROVIDER_LIST_URLS

    providers_cache = False
    try:
        from optimade.server import data

        if getattr(data, "providers", None) is not None:
            providers_cache = copy.deepcopy(data.providers)

        caplog.clear()
        with mock.patch("requests.get", side_effect=ConnectionError):
            del data.providers  # pylint: disable=no-member
            assert get_providers() == []

            warning_message = """Could not retrieve a list of providers!

    Tried the following resources:

{}
    The list of providers will not be included in the `/links`-endpoint.
""".format(
                "".join([f"    * {_}\n" for _ in PROVIDER_LIST_URLS])
            )
            assert warning_message in caplog.messages

    finally:
        if providers_cache:
            from optimade.server import data

            data.providers = providers_cache

            # Trying to import providers to make sure it's there again now
            from optimade.server.data import providers

            assert providers == providers_cache


def test_get_base_url():
    """
    This tests whether the base_url is correctly extracted from the request.
    """
    from optimade.server.routers.utils import get_base_url
    from optimade.server.config import CONFIG

    base_url_org = CONFIG.base_url
    root_path_org = CONFIG.root_path
    CONFIG.base_url = None
    CONFIG.root_path = "/optimade"
    request_urls = (
        "http://www.example.com",
        "http://www.example.com/",
        "http://www.example.com/optimade/v1/links",
        "http://www.structures.com/links",
        "https://www.links.org/optimade/structures/123456",
    )
    base_urls = (
        "http://www.example.com/optimade",
        "http://www.example.com/optimade",
        "http://www.example.com/optimade",
        "http://www.structures.com/optimade",
        "https://www.links.org/optimade",
    )
    results = []
    for request_url in request_urls:
        results.append(get_base_url(request_url))

    CONFIG.base_url = base_url_org
    CONFIG.root_path = root_path_org
    for i in range(len(base_urls)):
        assert results[i] == base_urls[i]
