# # # main.py
# # import os
# # from flask import jsonify, request
# # from werkzeug.utils import secure_filename

# # # Import your existing function
# # from stringart_public import generate_string_art

# # def process_image_request(request):
# #     """
# #     HTTP-triggered cloud function that wraps the string art engine.
# #     1. Validates the request.
# #     2. Saves the uploaded image to a temporary location.
# #     3. Calls the core string art generation logic.
# #     4. Returns the results as a JSON response.
# #     """
# #     # --- 1. Validate the request ---
# #     if request.method != 'POST':
# #         return 'Only POST requests are accepted', 405

# #     if 'image' not in request.files:
# #         return 'Missing "image" file in the request', 400

# #     uploaded_file = request.files['image']
# #     if uploaded_file.filename == '':
# #         return 'No selected file', 400

# #     # --- 2. Save image to the temporary directory ---
# #     # Cloud Functions can only write to the /tmp directory
# #     filename = secure_filename(uploaded_file.filename)
# #     temp_path = os.path.join('/tmp', filename)
# #     uploaded_file.save(temp_path)

# #     # --- 3. Call your engine ---
# #     try:
# #         results = generate_string_art(temp_path)
# #     except Exception as e:
# #         # If your engine fails, return a server error
# #         print(f"Error during string art generation: {e}")
# #         return "Internal server error during image processing", 500
# #     finally:
# #         # --- 4. Clean up the temporary file ---
# #         if os.path.exists(temp_path):
# #             os.remove(temp_path)

# #     # --- 5. Return JSON response ---
# #     return jsonify(results)

# # TEST
# # main.py
# import json
# import os
# import requests
# import shopify
# from flask import request
# from google.cloud import secretmanager

# # Import your existing function
# from stringart_public import generate_string_art

# # --- Helper function to get the secret ---
# # def get_shopify_secret():
# #     client = secretmanager.SecretManagerServiceClient()
# #     name = "projects/211687143240/secrets/shopify-api-password/versions/latest"
# #     response = client.access_secret_version(request={"name": name})
# #     return response.payload.data.decode("UTF-8")

# def process_image_request(request):
#     if not request.is_json:
#         return "Error: Request must be JSON.", 400

#     order_data = request.get_json()
#     print("Received webhook.")

#     try:
#         order_id = order_data.get('id')
#         if not order_id:
#             print("Could not find Order ID in payload.")
#             return "Error: Missing Order ID.", 400

#         image_url = None
#         if 'line_items' in order_data and len(order_data['line_items']) > 0:
#             properties = order_data['line_items'][0].get('properties', [])
#             for prop in properties:
#                 if prop.get('name') == 'Custom Image URL':
#                     image_url = prop.get('value')
#                     break
        
#         if image_url:
#             print(f"Found image URL: {image_url}")
#             response = requests.get(image_url, stream=True)
#             response.raise_for_status()
            
#             filename = "downloaded_image.jpg"
#             temp_path = os.path.join('/tmp', filename)
#             with open(temp_path, 'wb') as f: f.write(response.content)
            
#             results = generate_string_art(temp_path)
#             os.remove(temp_path)
#             print("String art generated successfully.")
#         else:
#             print("No image URL found. Generating placeholder note for test webhook.")
#             results = {
#                 "versions": [
#                     {
#                         "coordinates": ["No image URL provided in order data (This is expected for test notifications)."],
#                         "preview_b64": "N/A"
#                     }
#                 ]
#             }

#         # --- Connect to Shopify API using an Environment Variable ---
#         api_password = os.environ.get('SHOPIFY_API_PASSWORD')
#         if not api_password:
#             raise ValueError("SHOPIFY_API_PASSWORD environment variable not set")
            
#         shop_url = "ra2es3-rt.myshopify.com" 
#         api_version = '2025-07' 
        
#         session = shopify.Session(shop_url, api_version, api_password)
#         shopify.ShopifyResource.activate_session(session)

#         # --- This is the corrected section ---
#         order = shopify.Order.find(order_id)
#         note_content = f"String Art Coordinates: {results['versions'][0]['coordinates']}"
        
#         # 1. Get any existing notes
#         existing_note = order.note or ""
#         # 2. Append the new note
#         order.note = existing_note + "\n\n" + note_content.strip()
#         # 3. Save the entire order object
#         order.save()
        
#         print(f"Successfully added note to Order #{order.order_number}")

#         shopify.ShopifyResource.clear_session()
#         return "Successfully processed request.", 200

#     except Exception as e:
#         # This will print the actual, detailed error message if something fails
#         print(f"An error occurred: {e}")
#         return "An internal error occurred.", 500


# main.py
import os
from flask import jsonify, request, make_response
from werkzeug.utils import secure_filename

# Importeer je bestaande functie
from stringart_public import generate_string_art

def process_image_request(request):
    """
    HTTP-triggered cloud functie die de string art engine wrapt.
    Deze functie is ontworpen om direct vanuit een browser te worden aangeroepen.
    1. Valideert de request en de afbeelding.
    2. Slaat de geüploade afbeelding tijdelijk op.
    3. Roept de core string art logica aan.
    4. Geeft de resultaten terug als een JSON response met CORS headers.
    """
    # --- Belangrijk voor cross-origin requests vanuit de browser (Shopify -> GCP) ---
    if request.method == 'OPTIONS':
        # Handle preflight request for CORS
        headers = {
            'Access-Control-Allow-Origin': '*', # Of specifieker: 'https://jouw-winkel.myshopify.com'
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    # Zet de CORS header voor de daadwerkelijke response
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    # --- 1. Valideer de request ---
    if request.method != 'POST':
        return make_response(jsonify(error='Only POST requests are accepted'), 405, headers)

    if 'image' not in request.files:
        return make_response(jsonify(error='Missing "image" file in the request'), 400, headers)

    uploaded_file = request.files['image']
    if uploaded_file.filename == '':
        return make_response(jsonify(error='No selected file'), 400, headers)

    # --- 2. Sla afbeelding tijdelijk op ---
    # Cloud Functions kunnen alleen schrijven naar de /tmp directory
    filename = secure_filename(uploaded_file.filename)
    temp_path = os.path.join('/tmp', filename)
    uploaded_file.save(temp_path)

    # --- 3. Roep de engine aan ---
    try:
        results = generate_string_art(temp_path)
    except Exception as e:
        print(f"Error during string art generation: {e}")
        return make_response(jsonify(error="Internal server error during image processing"), 500, headers)
    finally:
        # --- 4. Ruim het tijdelijke bestand op ---
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # --- 5. Geef de JSON response terug ---
    return make_response(jsonify(results), 200, headers)