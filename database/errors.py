from peewee import IntegrityError


def is_unique_violation(error: IntegrityError) -> bool:
    msg = str(error).lower()
    return "unique" in msg
