def extract_pallet_contents(input_string):
    # Find the index of the first occurrence of a dash ('-')
    first_dash_index = input_string.find('-')
    
    # Extract two characters before the first dash
    first_pallet_content_start = first_dash_index - 1
    first_pallet_content_end = input_string.find(',', first_dash_index)
    
    # Extract the first pallet content
    first_pallet_content = input_string[first_pallet_content_start:first_pallet_content_end]
    
    # Extract the remaining contents after the first comma
    remaining_pallet_contents = input_string[first_pallet_content_end + 1:].split(',')
    
    # Combine the first pallet content with the remaining contents
    pallet_contents = [first_pallet_content] + remaining_pallet_contents
    
    # Clean up any extra spaces or trailing commas
    pallet_contents = [p.strip() for p in pallet_contents if p.strip()]
    
    return pallet_contents

# Example usage
input_string = "240058155320005301079801005815530050297329004435653370600373298005815530054241400HUB2507247021PREVIOUS533000010711109082415080825331000021433202-0009 / 18000,1-0009 / 18000,2-0010 / 17990,1-0010 / 17990,7-0011 / 18000,2-0011 / 18000,,,,,,,,,,,,,,,,,,"
pallet_contents = extract_pallet_contents(input_string)

for content in pallet_contents:
    print(content)