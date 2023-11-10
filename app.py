import streamlit as st
import openai
import base64
from io import BytesIO
from PIL import Image
import requests


# Set your OpenAI API key
openai.api_key = st.secrets['openai_key']

# Function to encode image to base64
def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to get image description from GPT-4 Vision API
def get_image_description(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": "Describe this image as detail as possible. The object position description should be exactly the same with the image. Do not mention about what kind of style use in this image for instance 'drawing','painting', etc. Just describe the object positions."
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    # return response.json().choices[0].message['content']
    # Check if the response was successful
    if response.status_code == 200:
        # Parse the response JSON and extract the description
        try:
            return response.json()['choices'][0]['message']['content']#['text']
        except KeyError as e:
            # If the expected keys are not in the JSON response, print the error
            st.error(f"KeyError: {str(e)} - the structure of the response JSON is not as expected.")
            return None
    else:
        # If the response is not OK, print the status code and content for debugging
        st.error(f"Failed to get description. Status Code: {response.status_code} - Response: {response.content}")
        return None


# Function to generate an image using DALL·E 3 API with the description
def generate_image_with_style(description, style):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"Create an photo-like image with {style} style and extremely detailed with natural lighting and photo-cinematic for this description: {description}. Remember create in {style} style and extremely detailed with natural lighting and photo-cinematic.",
        size="1792x1024",
        quality="hd",
        n=1
    )
    image_url = response.data[0].url
    return image_url

# Streamlit app
st.title('Kid Sketch Realizer')
st.subheader("Ubah gambar atau sketsa gambar putra/putri kesayangan bapak menjadi versi foto-realistis. Realisasikan imajinasi mereka. Pasang di ruang tamu dan spot-spot terbaik.")

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload foto gambar.", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Display the uploaded image
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    # Ask user for the desired style for image generation
    style = st.selectbox(
        'Which style would you like to apply?',
        ('Photorealistic', 'Matte Painting', 'Anime', 'Ghibli', 'Pencil Sketch')
    )

    if st.button('Describe & Generate'):
        # Encode the uploaded image to base64
        base64_image = encode_image_to_base64(image)
        # st.write(base64_image)

        with st.spinner('Analyzing the image...'):
            # Get a description of the image from GPT-4 Vision
            description = get_image_description(base64_image)
            # st.write(description)

        with st.spinner('Recreate image in new style...'):
            # Generate an image with the desired style using DALL·E
            generated_image_url = generate_image_with_style(description, style)

        # Display the generated image
        if generated_image_url:
            st.image(generated_image_url, caption='Generated Image.', use_column_width=True)
            st.write(description)
        else:
            st.error("An error occurred during image generation. Please try again.")
