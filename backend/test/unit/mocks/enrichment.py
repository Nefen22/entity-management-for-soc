from unittest.mock import MagicMock

def mock_city():
    city = MagicMock()

    city.country.iso_code = "US"
    city.country.name = "United States"

    city.city.name = "Chicago"

    city.subdivisions.most_specific.name = "Illinois"

    city.continent.code = "NA"

    city.location.latitude = 41.85
    city.location.longitude = -87.65
    city.location.time_zone = "America/Chicago"

    city.traits.network = "8.8.8.0/24"

    return city


def mock_asn():
    asn = MagicMock()
    asn.autonomous_system_number = 15169
    asn.autonomous_system_organization = "Google LLC"
    return asn