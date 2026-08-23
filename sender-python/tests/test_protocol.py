import json

from sender import protocol


def test_build_request_json_has_expected_fields():
    line = protocol.build_request_json("id-1", "HAMMING", 8, "0101010101010")
    data = json.loads(line)
    assert data == {
        "messageId": "id-1",
        "algorithm": "HAMMING",
        "originalBitLength": 8,
        "frameBits": "0101010101010",
    }


def test_parse_response_success():
    line = '{"messageId":"id-1","status":"OK","errorsDetected":0,"errorsCorrected":0,"message":"A"}'
    response = protocol.parse_response(line)
    assert response.status == "OK"
    assert response.message == "A"
    assert response.error is None


def test_parse_response_failure():
    line = ('{"messageId":"id-1","status":"ERROR_DETECTED","errorsDetected":1,'
            '"errorsCorrected":0,"message":null,"error":"CRC-32 no coincide"}')
    response = protocol.parse_response(line)
    assert response.status == "ERROR_DETECTED"
    assert response.message is None
    assert response.error == "CRC-32 no coincide"
