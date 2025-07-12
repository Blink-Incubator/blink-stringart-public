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
from flask import request

from stringart_public import generate_string_art

def process_image_request(request):
    """
    Final function to process Shopify order webhooks.
    """
    if not request.is_json:
        return "Error: Request must be JSON.", 400

    order_data = request.get_json()
    print("Received new order webhook.")

    try:
        # Navigate through the JSON to find the properties
        line_item = order_data['line_items'][0]
        properties = line_item.get('properties', [])

        image_url = None
        for prop in properties:
            if prop.get('name') == 'Custom Image URL':
                image_url = prop.get('value')
                break

        if not image_url:
            print("Error: 'Custom Image URL' property not found in line item.")
            return "Error: Image URL not found.", 400

        print(f"Found image URL: {image_url}")

        # Download the image from the URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the downloaded image to the temporary directory
        filename = image_url.split('/')[-1]
        temp_path = os.path.join('/tmp', filename)
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Image downloaded and saved to {temp_path}")

        # Call your string art engine
        results = generate_string_art(temp_path)
        print("String art generated successfully.")

        # Optional: Clean up the downloaded file
        os.remove(temp_path)

        # We don't need to return the JSON, just a success message
        # In a real app, you would now email the results or update the Shopify order.
        return "Successfully processed string art.", 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred.", 500