from datetime import datetime


def get_current_iso_week() -> str:
    now = datetime.now()
    year = now.strftime("%Y")
    week = int(now.strftime("%W")) + 1
    if week < 10:
        week = f"0{week}"
    return f"{year}{week}"
