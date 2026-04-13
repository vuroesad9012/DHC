import requests
import time

LTC_ADDRESS = "Lhn5q2eTHtWRi3jJymYZg7CQQeJWqXsXaG"

# Price mapping for each DHC amount
price_mapping = {
    "1 Million DHC": 0.50,
    "2 Million DHC": 1,
    "3 Million DHC": 1.50,
    "4 Million DHC": 2,
    "5 Million DHC": 2.50,
    "6 Million DHC": 3,
    "7 Million DHC": 3.50,
    "8 Million DHC": 4,
    "9 Million DHC": 4.50,
    "10 Million DHC": 5,
}


def check_ltc_payment(amount_dhc: str, timeout: int = 60):
    """
    Check if payment has been received for the specified DHC amount.
    Uses Blockchair API to check recent transactions to the LTC address.
    
    Args:
        amount_dhc: The DHC amount selected (e.g., "1 Million DHC")
        timeout: Maximum time to wait in seconds
        
    Returns:
        (bool, str) - (payment_found, message)
    """
    required_amount = price_mapping.get(amount_dhc, 0)
    
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Using Blockchair API to get address info
                url = f"https://blockchair.com/litecoin/address/{LTC_ADDRESS}"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Blockchair returns data in this format
                    if "data" in data and isinstance(data["data"], dict):
                        address_data = data["data"].get(LTC_ADDRESS, {})
                        
                        # Check if there are any transactions
                        if address_data.get("transaction_count", 0) > 0:
                            # Get the total received amount
                            total_received = address_data.get("received", 0) / 100000000  # Convert satoshis to LTC
                            
                            # For quick checking, we'll accept if total received meets requirement
                            if total_received >= required_amount:
                                return True, f"✅ Payment of {total_received} LTC detected!"
                
            except requests.exceptions.RequestException as e:
                pass
            except Exception as e:
                pass
            
            # Wait before retry
            time.sleep(5)
        
        return False, f"❌ Payment not found. Please ensure you sent exactly {required_amount} LTC to the address."
        
    except Exception as e:
        return False, f"❌ Error checking payment: {str(e)}"
