from datetime import datetime

from assistant.settings import CUSTOM_API_KEY


def get_date_string():
    now = datetime.now()
    return now.strftime('%m/%d/%Y')


# Function to check API key
def check_api_key(request) -> bool:
    api_key = request.headers.get('X-API-KEY')
    if api_key != CUSTOM_API_KEY:
        return False
    return True
