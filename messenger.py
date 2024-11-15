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
        return response.json()  # Returns the JSON response from the API
    else:
        print(f"API Error: {response.status_code}, {response.text}")
        return None

# Function to read the input data from a file and parse it
def read_input_file(filename):
    casualties = {}
    bed_list = []
    helicopter_list = []
    no_care_list = []

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()

                # Debugging output to see the line being processed
                print(f"Processing line: {line}")

                # Check for lines that contain "Casualty"
                if line.startswith("Casualty"):
                    parts = line.split(":")
                    casualty_number = int(parts[0].split()[1])  # Extract casualty number
                    details = parts[1].strip()  # The rest is the details

                    # Debugging output to check details extraction
                    print(f"Casualty number: {casualty_number}, Details: {details}")

                    # Check if the casualty is allocated to a bed
                    if "allocated to bed" in details:
                        bed_list.append(casualty_number)
                        blood_units = int(details.split("Required blood units:")[1].split()[0])
                        care_time = float(details.split("Required care time:")[1].split()[0])
                        survival_chance = float(details.split("Survival chance:")[1].split()[0])
                        casualties[casualty_number] = {
                            "status": "bed", 
                            "blood": blood_units,
                            "care_time": care_time,
                            "survival_chance": survival_chance
                        }

                    # Check if the casualty is allocated to a helicopter
                    elif "allocated to helicopter" in details:
                        helicopter_list.append(casualty_number)
                        blood_units = int(details.split("Required blood units:")[1].split()[0])
                        survival_chance = float(details.split("Survival with care:")[1].split()[0])
                        casualties[casualty_number] = {
                            "status": "helicopter", 
                            "blood": blood_units,
                            "survival_chance": survival_chance
                        }

                    # Check if the casualty received no care
                    elif "received no care" in details:
                        no_care_list.append(casualty_number)
                        survival_without_care = float(details.split("Survival without care:")[1].split()[0])
                        casualties[casualty_number] = {
                            "status": "no care", 
                            "survival_without_care": survival_without_care
                        }

    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

    # Debugging output to show lists and casualties
    print(f"Bed List: {bed_list}")
    print(f"Helicopter List: {helicopter_list}")
    print(f"No Care List: {no_care_list}")
    print(f"Casualties: {casualties}")

    return casualties, bed_list, helicopter_list, no_care_list

# Function to create custom message for nurses
def generate_nurse_message(casualties, bed_list, helicopter_list, no_care_list):
    nurse_message = "Here are the new patient plans:\n"
    nurse_message += f"Patients allocated to beds: {bed_list}\n"
    nurse_message += f"Patients allocated to helicopter: {helicopter_list}\n"
    nurse_message += f"Patients receiving no care: {no_care_list}\n"

    for casualty in casualties:
        if casualties[casualty]["status"] == "bed":
            nurse_message += f"Casualty {casualty}: Blood units needed: {casualties[casualty]['blood']}, Care time: {casualties[casualty]['care_time']} hours, Survival chance: {casualties[casualty]['survival_chance']}\n"
        elif casualties[casualty]["status"] == "helicopter":
            nurse_message += f"Casualty {casualty}: Blood units needed: {casualties[casualty]['blood']}, Survival chance with care: {casualties[casualty]['survival_chance']}\n"
        elif casualties[casualty]["status"] == "no care":
            nurse_message += f"Casualty {casualty}: Survival chance without care: {casualties[casualty]['survival_without_care']}\n"

    return nurse_message

# Function to create custom message for the person managing blood resources
def generate_blood_message(casualties, total_blood_available=30):
    total_blood_needed = sum([casualties[casualty]["blood"] for casualty in casualties if casualties[casualty]["status"] in ["bed", "helicopter"]])
    blood_message = f"Total blood units needed: {total_blood_needed}\n"

    blood_message += "Blood allocation per casualty:\n"
    for casualty in casualties:
        if casualties[casualty]["status"] in ["bed", "helicopter"]:
            blood_message += f"Casualty {casualty}: {casualties[casualty]['blood']} units\n"

    blood_remaining = total_blood_available - total_blood_needed
    blood_message += f"Blood remaining: {blood_remaining} units\n"

    return blood_message

# Function to write the generated messages to a text file
def write_report_to_file(nurse_message, blood_message, output_filename="casualty_report.txt"):
    try:
        with open(output_filename, 'w') as file:
            file.write(nurse_message)
            file.write("\n\n")  # Adding space between messages
            file.write(blood_message)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

# Example usage
filename = 'output.txt'  # Path to your input text file
casualties, bed_list, helicopter_list, no_care_list = read_input_file(filename)

# Generate messages
nurse_message = generate_nurse_message(casualties, bed_list, helicopter_list, no_care_list)
blood_message = generate_blood_message(casualties)

# Optionally, use the API to process the message (for example, summarizing or enhancing the message)
api_response = call_nipr_api(nurse_message)
if api_response:
    print(f"API Response: {api_response}")
else:
    print("API request failed.")

# Write messages to a text file
write_report_to_file(nurse_message, blood_message)

# Optionally print the messages for confirmation
print("Message for Nurse:\n", nurse_message)
print("\nMessage for Blood Manager:\n", blood_message)
