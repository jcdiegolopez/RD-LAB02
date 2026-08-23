import json
from dataclasses import dataclass


@dataclass(frozen=True)
class FrameResponse:
    message_id: str
    status: str
    errors_detected: int
    errors_corrected: int
    message: str | None
    error: str | None


def build_request_json(message_id: str, algorithm: str, original_bit_length: int, frame_bits: str) -> str:
    return json.dumps({
        "messageId": message_id,
        "algorithm": algorithm,
        "originalBitLength": original_bit_length,
        "frameBits": frame_bits,
    })


def parse_response(line: str) -> FrameResponse:
    data = json.loads(line)
    return FrameResponse(
        message_id=data.get("messageId"),
        status=data.get("status"),
        errors_detected=int(data.get("errorsDetected", 0)),
        errors_corrected=int(data.get("errorsCorrected", 0)),
        message=data.get("message"),
        error=data.get("error"),
    )
