import requests
import os

# Gamepass ID mapping for each DHC amount
GAMEPASS_IDS = {
    "1 Million DHC": int(os.getenv("GAMEPASS_ID_1M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "2 Million DHC": int(os.getenv("GAMEPASS_ID_2M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "3 Million DHC": int(os.getenv("GAMEPASS_ID_3M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "4 Million DHC": int(os.getenv("GAMEPASS_ID_4M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "5 Million DHC": int(os.getenv("GAMEPASS_ID_5M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "6 Million DHC": int(os.getenv("GAMEPASS_ID_6M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "7 Million DHC": int(os.getenv("GAMEPASS_ID_7M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "8 Million DHC": int(os.getenv("GAMEPASS_ID_8M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "9 Million DHC": int(os.getenv("GAMEPASS_ID_9M", "0")) or int(os.getenv("GAMEPASS_ID")),
    "10 Million DHC": int(os.getenv("GAMEPASS_ID_10M", "0")) or int(os.getenv("GAMEPASS_ID")),
}

# Fallback for old setup if only GAMEPASS_ID is set
GAMEPASS_ID = int(os.getenv("GAMEPASS_ID", "0"))


# Convert username to userId
def get_user_id(username):
    url = "https://users.roblox.com/v1/usernames/users"
    data = {
        "usernames": [username],
        "excludeBannedUsers": True
    }

    r = requests.post(url, json=data)
    if r.status_code == 200:
        data = r.json()
        if data["data"]:
            return data["data"][0]["id"]
    return None


# Check gamepass ownership for a specific amount
def owns_gamepass(user_id, dhc_amount: str = None):
    """
    Check if user owns the gamepass for the specified DHC amount.
    
    Args:
        user_id: The Roblox user ID
        dhc_amount: The DHC amount (e.g., "1 Million DHC"). If None, uses default GAMEPASS_ID.
    
    Returns:
        Boolean indicating if user owns the gamepass
    """
    gamepass_id = GAMEPASS_IDS.get(dhc_amount, GAMEPASS_ID) if dhc_amount else GAMEPASS_ID
    
    if not gamepass_id or gamepass_id == 0:
        return False
    
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/GamePass/{gamepass_id}"
    r = requests.get(url)

    if r.status_code == 200:
        data = r.json()
        return len(data.get("data", [])) > 0

    return False
