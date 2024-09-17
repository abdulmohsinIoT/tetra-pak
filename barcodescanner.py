import evdev
import pyudev
import time

# A basic key mapping for barcode scanning (expand this as needed)
key_map = {
    'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
    'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
    'KEY_A': 'A', 'KEY_B': 'B', 'KEY_C': 'C', 'KEY_D': 'D', 'KEY_E': 'E',
    'KEY_F': 'F', 'KEY_G': 'G', 'KEY_H': 'H', 'KEY_I': 'I', 'KEY_J': 'J',
    'KEY_K': 'K', 'KEY_L': 'L', 'KEY_M': 'M', 'KEY_N': 'N', 'KEY_O': 'O',
    'KEY_P': 'P', 'KEY_Q': 'Q', 'KEY_R': 'R', 'KEY_S': 'S', 'KEY_T': 'T',
    'KEY_U': 'U', 'KEY_V': 'V', 'KEY_W': 'W', 'KEY_X': 'X', 'KEY_Y': 'Y',
    'KEY_Z': 'Z',
    'KEY_F1': 'F1', 'KEY_F2': 'F2', 'KEY_F3': 'F3', 'KEY_F4': 'F4',
    'KEY_F5': 'F5', 'KEY_F6': 'F6', 'KEY_F7': 'F7', 'KEY_F8': 'F8',
    'KEY_F9': 'F9', 'KEY_F10': 'F10', 'KEY_F11': 'F11', 'KEY_F12': 'F12',
    'KEY_LEFT': '<', 'KEY_RIGHT': '>', 'KEY_UP': '^', 'KEY_DOWN': 'v',
    'KEY_ENTER': '\n', 'KEY_SPACE': ' ', 'KEY_TAB': '\t',
    'KEY_MINUS': '-', 'KEY_EQUAL': '=', 'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']',
    'KEY_BACKSLASH': '\\', 'KEY_SEMICOLON': ';', 'KEY_APOSTROPHE': "'",
    'KEY_GRAVE': '`', 'KEY_COMMA': ',', 'KEY_DOT': '.', 'KEY_SLASH': '/',
    'KEY_CAPSLOCK': 'CAPSLOCK', 'KEY_NUMLOCK': '',  # Ignore NUMLOCK
    'KEY_SCROLLLOCK': 'SCROLLLOCK',
    'KEY_ESC': 'ESC', 'KEY_BACKSPACE': 'BACKSPACE', 'KEY_INSERT': 'INSERT',
    'KEY_DELETE': 'DELETE', 'KEY_HOME': 'HOME', 'KEY_END': 'END', 'KEY_PAGEUP': 'PAGEUP',
    'KEY_PAGEDOWN': 'PAGEDOWN', 'KEY_UP': 'UP', 'KEY_DOWN': 'DOWN', 'KEY_LEFT': 'LEFT',
    'KEY_RIGHT': 'RIGHT', 'KEY_PRINT': 'PRINT', 'KEY_PAUSE': 'PAUSE',
    'KEY_LCTRL': 'LCTRL', 'KEY_LSHIFT': 'LSHIFT', 'KEY_LALT': 'LALT', 'KEY_LGUI': 'LGUI',
    'KEY_RCTRL': 'RCTRL', 'KEY_RSHIFT': 'RSHIFT', 'KEY_RALT': 'RALT', 'KEY_RGUI': 'RGUI',
    'KEY_APPLICATION': 'APPLICATION', 'KEY_POWER': 'POWER',
    'KEY_HELP': 'HELP', 'KEY_MENU': 'MENU', 'KEY_SELECT': 'SELECT',
}

def extract_data(s):
    marker = 'FNC103'
    first_dash = s.find('-')
    second_dash = s.find('-', first_dash + 1)
    if second_dash == -1:
        return {"message": "Second dash not found", "success": False}
    start_of_interest = second_dash + 5
    marker_index = s.find(marker)
    if marker_index == -1:
        return {"message": "Marker not found", "success": False}
    count = s[start_of_interest:marker_index]
    production_order_start = marker_index + len(marker)
    raw_production_order = s[production_order_start:production_order_start + 11]
    production_order = f"P{raw_production_order[:3]}-{raw_production_order[4:]}"
    reel_number_start = production_order_start + 11
    raw_reel_number = s[reel_number_start:reel_number_start + 6]
    reel_number = f"{int(raw_reel_number[:2])}-{raw_reel_number[2:]}"
    return {'var_count': count, 'production_order': production_order, 'reel_number': reel_number, "success": True}


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

    first_10_chars = input_string[:10]
    
    # Remove the first 3 characters from this substring
    modified_chars = first_10_chars[3:]
    
    return {"pallet_contents": pallet_contents, "production_order": "P552-"+modified_chars, "success": True}

def find_device(vendor_id, product_id):
    context = pyudev.Context()
    for device in context.list_devices(subsystem='usb'):
        if vendor_id in device.get('ID_VENDOR_ID', '') and product_id in device.get('ID_MODEL_ID', ''):
            for child in device.children:
                if child.device_node and 'event' in child.device_node:
                    return child.device_node
    return None

vendor_id = '8888'
product_id = '2019'

def wait_for_device(vendor_id, product_id):
    while True:
        device_path = find_device(vendor_id, product_id)
        if device_path:
            return device_path
        else:
            print("Device not found. Waiting for reconnect...")
            time.sleep(5)  # Wait before trying again

while True:
    device_path = wait_for_device(vendor_id, product_id)
    device = evdev.InputDevice(device_path)
    print(f"Opened device {device.name} at {device_path}")

    try:
        device.grab()
        print("Device grabbed successfully.")
    except IOError as e:
        print(f"Error grabbing device: {e}")

    print("Listening for input...")
    barcode = ""

    try:
        reel_data = []
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                if key_event.keystate == key_event.key_down:
                    key = key_event.keycode
                    if key in key_map:
                        if key == 'KEY_ENTER':
                            print(f"Scanned barcode: {barcode}")
                            print((f"Length: {len(barcode)}"))
                            small = extract_data(barcode)
                            if(small['success'] != True):
                                contents = extract_pallet_contents(barcode)
                                print(contents)
                                print(f"production_order {contents['production_order']}")
                                for content in contents["pallet_contents"]:
                                    print(content)
                            else:
                                print(small)
                                reel_data.append(small)
                                print(reel_data)
                            small = ""
                            barcode = ""
                        else:
                            barcode += key_map[key]
    except OSError:
        print("Device removed or error occurred. Waiting for reconnect...")