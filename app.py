from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# Function to send images to Hugging Face
def send_image_to_huggingface(person_image_url, dress_image_url):
    endpoint_url = "https://huggingface.co/spaces/Kwai-Kolors/Kolors-Virtual-Try-On"
    data = {
        'data': [
            person_image_url,  # Person's image URL
            dress_image_url    # Dress image URL
        ]
    }
    response = requests.post(endpoint_url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['data'][0]  # Image result from Hugging Face API
    else:
        return None

@app.route('/webhook', methods=['GET','POST'])
def whatsapp():
    # Get incoming message details from Twilio
    incoming_msg = request.values.get('Body', '').lower()
    media_url_person = request.values.get('MediaUrl0', None)  # Person's image
    media_url_dress = request.values.get('MediaUrl1', None)   # Dress image

    # Respond to user via Twilio WhatsApp
    resp = MessagingResponse()
    msg = resp.message()

    if media_url_person and media_url_dress:
        # Process try-on using Hugging Face
        output_image = send_image_to_huggingface(media_url_person, media_url_dress)

        if output_image:
            msg.body("Here's your virtual try-on result!")
            msg.media(output_image)  # Send processed image back to user
        else:
            msg.body("Sorry, there was an issue processing your try-on. Please try again.")
    else:
        msg.body("Please send 2 images: one of yourself and one of the dress.")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
