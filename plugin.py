#Import the needed libraries
import requests
import json
from flask import Flask, request, send_from_directory
from datetime import datetime

# API used to fetch the data from OpenSea 
# Documentation: https://docs.opensea.io/reference/api-overview
OPENSEA_URL="https://api.opensea.io/api/v2/events?limit=1"
api_key=  "opensea-api-key" #replace with your key

#Initialize the Flask app
app = Flask(__name__)

# This code snippet defines a route /opensea/latest using Flask's @app.route decorator 
# for handling GET requests. It sends a GET request to a specified URL (OPENSEA_URL) with 
# custom headers including an API key, retrieves JSON data from the response, processes it using the 
# aggregate_user_friendly function, and returns a message based on the processed data.
@app.route('/opensea/latest', methods=['GET'])
def opensea():
    
    headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json" }
    response = requests.get(OPENSEA_URL,headers=headers)
    api_data = response.json()
    message = aggregate_user_friendly(api_data)
    return message


# Default route populated to show things are working when we deploy and test
@app.route("/")
def index():
    return "The plugin is working"

def aggregate_user_friendly(data):
  result = []

  for event in data['asset_events']:
    # Aggregate event details
    event_details = f"Event Type: {event['event_type'].capitalize()}\n"
    event_details += f"Order Type: {event['order_type'].capitalize()}\n"
    event_details += f"Chain: {event['chain'].capitalize()}\n"
    
    # Convert timestamp to readable date
    date = datetime.fromtimestamp(event['event_timestamp'])
    event_details += f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    event_details += f"Maker: {event['maker']}\n"
    event_details += f"Order Hash: {event['order_hash']}\n"
    
    # Add start and expiration dates if available
    if 'start_date' in event:
      start_date = datetime.fromtimestamp(event['start_date'])
      event_details += f"Start Date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if 'expiration_date' in event:
      exp_date = datetime.fromtimestamp(event['expiration_date'])
      event_details += f"Expiration Date: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Aggregate asset or NFT details if available
    item = event.get('asset') or event.get('nft')
    if item:
      item_details = f"\nItem Details:\n"
      item_details += f"Collection: {item.get('collection', 'N/A')}\n"
      item_details += f"Token ID: {item.get('identifier', 'N/A')}\n"
      item_details += f"Contract: {item.get('contract', 'N/A')}\n"
      item_details += f"Token Standard: {item.get('token_standard', 'N/A').upper()}\n"
      item_details += f"OpenSea URL: {item.get('opensea_url', 'N/A')}\n"
      
      if item.get('image_url'):
        item_details += f"Image URL: {item['image_url']}\n"
      
      item_details += f"Last Updated: {item.get('updated_at', 'N/A')}\n"
      item_details += f"Disabled: {'Yes' if item.get('is_disabled', False) else 'No'}\n"
      item_details += f"NSFW: {'Yes' if item.get('is_nsfw', False) else 'No'}\n"
      
      event_details += item_details
    else:
      event_details += "\nNo item details available\n"

    # Add payment details if available
    if 'payment' in event:
      payment = event['payment']
      payment_details = f"\nPayment Details:\n"
      payment_details += f"Quantity: {payment['quantity']}\n"
      payment_details += f"Token: {payment['symbol']}\n"
      payment_details += f"Token Address: {payment['token_address']}\n"
      event_details += payment_details

  result.append(event_details)

  # Aggregate next page token
  next_token = f"\nNext Page Token: {data['next']}"
  result.append(next_token)

  return "\n".join(result)
