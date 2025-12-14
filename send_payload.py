import json
import requests

# ---------------- CONFIG ----------------
BACKEND_URL = "http://localhost:7000"  # your server API
PAYLOAD_FILE = "payload.json"          # path to your JSON
# ----------------------------------------

def main():
    # Load JSON payload
    with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)

    try:
        response = requests.post(
            BACKEND_URL,
            json=payload,  # requests automatically sets Content-Type: application/json
            timeout=300
            )
        response.raise_for_status()  # raises HTTPError if 400/500

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return

    # Print backend response
    print("✅ Response from server:")
    print(response.text)


if __name__ == "__main__":
    main()
