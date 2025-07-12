# # main.py
# import os
# from flask import jsonify, request
# from werkzeug.utils import secure_filename

# # Import your existing function
# from stringart_public import generate_string_art

# def process_image_request(request):
#     """
#     HTTP-triggered cloud function that wraps the string art engine.
#     1. Validates the request.
#     2. Saves the uploaded image to a temporary location.
#     3. Calls the core string art generation logic.
#     4. Returns the results as a JSON response.
#     """
#     # --- 1. Validate the request ---
#     if request.method != 'POST':
#         return 'Only POST requests are accepted', 405

#     if 'image' not in request.files:
#         return 'Missing "image" file in the request', 400

#     uploaded_file = request.files['image']
#     if uploaded_file.filename == '':
#         return 'No selected file', 400

#     # --- 2. Save image to the temporary directory ---
#     # Cloud Functions can only write to the /tmp directory
#     filename = secure_filename(uploaded_file.filename)
#     temp_path = os.path.join('/tmp', filename)
#     uploaded_file.save(temp_path)

#     # --- 3. Call your engine ---
#     try:
#         results = generate_string_art(temp_path)
#     except Exception as e:
#         # If your engine fails, return a server error
#         print(f"Error during string art generation: {e}")
#         return "Internal server error during image processing", 500
#     finally:
#         # --- 4. Clean up the temporary file ---
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#     # --- 5. Return JSON response ---
#     return jsonify(results)

# TEST
# main.py
import json
import os
import requests
import shopify
from flask import request
from google.cloud import secretmanager

# Import your existing function
from stringart_public import generate_string_art

# --- Helper function to get the secret ---
def get_shopify_secret():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/211687143240/secrets/shopify-api-password/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def process_image_request(request):
    if not request.is_json:
        return "Error: Request must be JSON.", 400

    order_data = request.get_json()
    print("Received webhook.")

    try:
        order_id = order_data.get('id')
        if not order_id:
            print("Could not find Order ID in payload.")
            return "Error: Missing Order ID.", 400

        # --- Try to find the image URL ---
        image_url = None
        if 'line_items' in order_data and len(order_data['line_items']) > 0:
            properties = order_data['line_items'][0].get('properties', [])
            for prop in properties:
                if prop.get('name') == 'Custom Image URL':
                    image_url = prop.get('value')
                    break
        
        # --- Process image if URL is found, otherwise create a placeholder result ---
        if image_url:
            print(f"Found image URL: {image_url}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            filename = "downloaded_image.jpg"
            temp_path = os.path.join('/tmp', filename)
            with open(temp_path, 'wb') as f: f.write(response.content)
            
            results = generate_string_art(temp_path)
            os.remove(temp_path)
            print("String art generated successfully.")
        else:
            print("No image URL found. Generating placeholder note for test webhook.")
            results = {
                "versions": [
                    {
                        "coordinates": ["No image URL provided in order data (This is expected for test notifications)."],
                        "preview_b64": "N/A"
                    }
                ]
            }

        # --- Connect to Shopify API ---
        api_password = get_shopify_secret()
        shop_url = "ra2es3-rt.myshopify.com" 
        api_version = '2025-07' 
        
        session = shopify.Session(shop_url, api_version, api_password)
        shopify.ShopifyResource.activate_session(session)

        # --- Add Note to the Order ---
        order = shopify.Order.find(order_id)
        note_content = f"String Art Coordinates: {results['versions'][0]['coordinates']}"
        order.add_note(note_content)
        print(f"Successfully added note to Order #{order.order_number}")

        shopify.ShopifyResource.clear_session()
        return "Successfully processed request.", 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred.", 500