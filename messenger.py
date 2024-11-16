import requests
import json

# Set your NiprGPT API details
url = "https://hackathon.niprgpt.mil/llama/v1/chat/completions"
headers = {
    "Authorization": "Bearer Y2VudGNvbTpsZXRtZWlu",  # Replace with your actual API key
    "Content-Type": "application/json"
}

# Function to use NiprGPT API
def call_nipr_api(message):
    data = {
        "model": "neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",  # Model as per the resource
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7  # Adjusting temperature for response variability
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']  # Returns the refined message
    else:
        print(f"API Error: {response.status_code}, {response.text}")
        return None

# Function to read the entire input data from a file
def read_input_file(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()  # Read the entire file content as a string
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

# Function to write refined messages to a file (for healthcare professional)
def write_message_to_file(message, output_filename="healthcare_report.txt"):
    try:
        with open(output_filename, 'w') as file:
            file.write(message)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# Function to write refined messages to a file (for blood manager)
def write_blood_message_to_file(blood_message, output_filename="blood_report.txt"):
    try:
        with open(output_filename, 'w') as file:
            file.write(blood_message)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# Example usage
filename = 'output.txt'  # Path to your input text file

# Read the entire contents of the file (output.txt)
file_content = read_input_file(filename)

if file_content:
    # Send the entire file content to the NiprGPT API for refinement
    refined_message = call_nipr_api(file_content)
    
    # If the API returns a refined message, write it to the respective file
    if refined_message:
        # You can split the output into two parts (for nurse and blood manager)
        # For this example, we'll assume the response is split based on a specific format or section
        # You may need to adjust this depending on how the API response is structured.
        
        # Example of how you can split the response into nurse and blood manager messages
        # For simplicity, I'm writing the entire message into both files (you can further refine this logic):
        write_message_to_file(refined_message, "healthcare_report.txt")
        write_blood_message_to_file(refined_message, "blood_report.txt")
        
        print("Refined message for Nurse and Blood Manager has been written to files.")
    else:
        print("Failed to get a refined message from the API.")
else:
    print("Failed to read the input file.")
