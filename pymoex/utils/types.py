def safe_date(value):
    if not value or value == "0000-00-00":
        return None
    return value
