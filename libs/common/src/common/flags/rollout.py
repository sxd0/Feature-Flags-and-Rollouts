import hashlib

def is_in_rollout(flag_key: str, env: str, user_id: str, rollout_percentage: int) -> bool:
    if rollout_percentage <= 0:
        return False
    if rollout_percentage >= 100:
        return True

    data = f"{flag_key}:{env}:{user_id}".encode("utf-8")
    digest = hashlib.sha256(data).digest()
    bucket = int.from_bytes(digest[:4], "big") % 100
    return bucket < rollout_percentage
