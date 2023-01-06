def format(number: int) -> str:
    """Return the number with a , between each 3 digits"""
    return "{0:,}".format(number)


def format_seconds(seconds):
    """
    Converts seconds to days, hours, minutes, and seconds.
    """
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}j {hours}h {minutes}m {seconds}s"
