import pytest

from tests.client import client


@pytest.mark.slow
def test_invalid_file_response(faviconico):
    response = client.post("/api/v1/via/itineraries/all", files={"xml_file": faviconico})
    print(response.url)
    assert response.status_code == 400


@pytest.mark.slow
def test_all_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/all", files={"xml_file": rsvia3xml})
    print(response.url)
    assert response.status_code == 200


@pytest.mark.slow
def test_specified_empty_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/specified", files={"xml_file": rsvia3xml})
    assert response.status_code == 422


@pytest.mark.slow
def test_specified_empty_destination_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/specified?source=DXB", files={"xml_file": rsvia3xml})
    assert response.status_code == 422


@pytest.mark.slow
def test_specified_empty_source_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/specified?destination=BKK", files={"xml_file": rsvia3xml})
    assert response.status_code == 422


@pytest.mark.slow
def test_specified_itinerary_response(rsvia3xml):
    response = client.post(
        "/api/v1/via/itineraries/specified?source=DXB&destination=BKK", files={"xml_file": rsvia3xml}
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_specified_itinerary_direct_response(rsvia3xml):
    response = client.post(
        "/api/v1/via/itineraries/specified?source=DXB&destination=BKK&direct=True", files={"xml_file": rsvia3xml}
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_specified_itinerary_transit_response(rsvia3xml):
    response = client.post(
        "/api/v1/via/itineraries/specified?source=DXB&destination=BKK&transit=True", files={"xml_file": rsvia3xml}
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_specified_itinerary_direct_and_transit_response(rsvia3xml):
    response = client.post(
        "/api/v1/via/itineraries/specified?source=DXB&destination=BKK&direct=True&transit=True",
        files={"xml_file": rsvia3xml},
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_optimal_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/optimal", files={"xml_file": rsvia3xml})
    assert response.status_code == 200


@pytest.mark.slow
def test_most_expensive_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/most_expensive", files={"xml_file": rsvia3xml})
    assert response.status_code == 200


@pytest.mark.slow
def test_cheapest_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/cheapest", files={"xml_file": rsvia3xml})
    assert response.status_code == 200


@pytest.mark.slow
def test_longest_two_side_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/longest", files={"xml_file": rsvia3xml})
    assert response.status_code == 200


@pytest.mark.slow
def test_shortest_two_side_response(rsvia3xml):
    response = client.post("/api/v1/via/itineraries/shortest", files={"xml_file": rsvia3xml})
    assert response.status_code == 200
    

@pytest.mark.slow
def test_longest_one_side_response(rsviaowxml):
    response = client.post("/api/v1/via/itineraries/longest", files={"xml_file": rsviaowxml})
    assert response.status_code == 200


@pytest.mark.slow
def test_shortest_one_side_response(rsviaowxml):
    response = client.post("/api/v1/via/itineraries/shortest", files={"xml_file": rsviaowxml})
    assert response.status_code == 200


@pytest.mark.slow
def test_difference_empty_response(rsvia3xml, rsviaowxml):
    response = client.post(
        "/api/v1/via/itineraries/difference", files={"first_xml_file": rsvia3xml, "second_xml_file": rsviaowxml}
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_difference_diff_response(rsvia3xml, rsviaowxml):
    response = client.post(
        "/api/v1/via/itineraries/difference?itineraries=diff",
        files={"first_xml_file": rsvia3xml, "second_xml_file": rsviaowxml},
    )
    assert response.status_code == 200


@pytest.mark.slow
def test_difference_all_response(rsvia3xml, rsviaowxml):
    response = client.post(
        "/api/v1/via/itineraries/difference?itineraries=all",
        files={"first_xml_file": rsvia3xml, "second_xml_file": rsviaowxml},
    )
    assert response.status_code == 200
