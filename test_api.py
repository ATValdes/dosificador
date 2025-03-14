import requests

BASE_URL = "http://127.0.0.1:8000/"

def test_get_config():
    # The API endpoint
    url = f"{BASE_URL}config"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_patch_basic_config():
    url = f"{BASE_URL}basic-config"

    data = {
        "reschedule_hours": {
            "normal": 24,
            "esto no deberia estar": "hola"
        }

    }

    response = requests.patch(url, json=data)
    print(response)

def test_patch_config():
    url = f"{BASE_URL}config"

    data = {
        "test-config": {
            "normal": 20,
            "error": 10
        },
        "test2": True,
        "test3": "hola",
        "test4": "mas test"

    }

    response = requests.patch(url, json=data)
    print(response)

def test_log_full():
    # The API endpoint
    url = f"{BASE_URL}log/full"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_log_text():
    # The API endpoint
    url = f"{BASE_URL}log/text"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_log_photos():
    # The API endpoint
    url = f"{BASE_URL}log/photos"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response)

def test_post_capture():
    # The API endpoint
    url = f"{BASE_URL}camera/capture"

    # A GET request to the API
    response = requests.post(url)

    # Print the response
    print(response.json())

def test_get_last_image():
    # The API endpoint
    url = f"{BASE_URL}camera/last-image"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def get_photo():
    url = f"{BASE_URL}camera/photo/test.jpg"

    response = requests.get(url)

    print(response.json())

def test_get_health():
    # The API endpoint
    url = f"{BASE_URL}health"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_get_water_status():
    # The API endpoint
    url = f"{BASE_URL}water-status"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_analyze_photo(photo_name: str):
    # The API endpoint
    url = f"{BASE_URL}analyze/image/{photo_name}"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_analyze_last_photo():
    # The API endpoint
    url = f"{BASE_URL}analyze/last-image"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_clear_schedule():
    # The API endpoint
    url = f"{BASE_URL}scheduler/clear-jobs"

    # A GET request to the API
    response = requests.post(url)

    # Print the response
    print(response.json())

def test_run_job():
    # The API endpoint
    url = f"{BASE_URL}scheduler/run-job"

    # Data
    data = {
        "script": "main.py",
        "minutes": 5
    }

    # A GET request to the API
    response = requests.post(url, json=data)

    # Print the response
    print(response.json())

def test_list_job():
    # The API endpoint
    url = f"{BASE_URL}scheduler/list-jobs"

    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

def test_home():
    # The API endpoint
    url = BASE_URL
    # A GET request to the API
    response = requests.get(url)

    # Print the response
    print(response.json())

# test_get_config()
# test_patch_basic_config()
# test_patch_config()
# test_log_full()
# test_log_text()
# test_log_photos()
# test_post_capture()
get_photo()
# test_get_last_image()
# test_get_health()
# test_get_water_status()
# test_analyze_photo("test.jpg")
# test_analyze_last_photo()
# test_run_job()
# test_list_job()
# test_clear_schedule()
# test_list_job()
# test_home()