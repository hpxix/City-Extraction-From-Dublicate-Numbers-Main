import pandas as pd
import json
import re

# Read both sheets of the Excel file
df_duplicated = pd.read_excel("chats298.xlsx", sheet_name="Input")
df_numbers = pd.read_excel("chats298.xlsx", sheet_name="Output")

# Load target IDs from JSON file
with open("city.json", "r", encoding="utf-8") as json_file:
    target_ids = json.load(json_file)

# Compile regular expressions for city names
# Create regular expression patterns for matching city names
# City names are extracted from the JSON data and compiled into regular expression patterns
city_names_ar = [city["label"] for city in target_ids]
city_names_en = [city["value"] for city in target_ids]
city_patterns_ar = re.compile(
    '|'.join(map(re.escape, city_names_ar)), re.IGNORECASE)
city_patterns_en = re.compile(
    '|'.join(map(re.escape, city_names_en)), re.IGNORECASE)

# Function to extract cities from chat content using regular expressions
# This function takes chat content as input and uses the compiled regular expressions
# to find and extract city names in both Arabic and English.
def extract_cities(chat_content):
    matched_cities_ar = city_patterns_ar.findall(chat_content)
    matched_cities_en = city_patterns_en.findall(chat_content)
    chat_cities = matched_cities_ar + matched_cities_en
    return chat_cities

# Create an empty dictionary to store extracted cities for each phone number
# This dictionary will be used to store extracted cities associated with each phone number.
extracted_cities_dict = {}

# Iterate through each duplicate phone number
# Iterate through the 'mobile2' column of the 'df_duplicated' DataFrame to process each duplicate phone number.
for number in df_duplicated['mobile2']:
    if number not in extracted_cities_dict:
        extracted_cities = []

        # Iterate through chat contents associated with the current phone number
        # Iterate through chat contents in the 'content' column of 'df_duplicated'
        # that are associated with the current phone number.
        for chat_content in df_duplicated[df_duplicated['mobile2'] == number]['content']:
            if isinstance(chat_content, str):
                extracted_cities.extend(extract_cities(chat_content))

        # Store the extracted cities for the current phone number in the dictionary.
        extracted_cities_dict[number] = extracted_cities

# Create a new DataFrame for non-duplicate numbers and extracted cities
# Create a new DataFrame 'new_df' to store non-duplicate phone numbers and their extracted cities.
new_data = []
for number in df_numbers['Mobile2']:
    if number not in extracted_cities_dict:
        new_data.append([number, ''])
    else:
        cities = extracted_cities_dict[number]
        new_data.append([number, ', '.join(cities)])

new_df = pd.DataFrame(new_data, columns=['Mobile2', 'ExtractedCities'])

merged_df = pd.merge(df_numbers, new_df, how='left', left_on='Mobile2', right_on='Mobile2')

# Save the new DataFrame to a new sheet in the same Excel file
# Use the 'pd.ExcelWriter' context manager to append 'new_df' to a new sheet named 'NewSheet'
# in the same Excel file.
with pd.ExcelWriter("chats298.xlsx", engine='openpyxl') as writer:
    merged_df.to_excel(writer, sheet_name="Output", index=False)


