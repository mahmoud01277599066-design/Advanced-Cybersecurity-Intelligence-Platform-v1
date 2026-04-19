import json
import os
from datetime import datetime

def save_output_to_json(data, component_name):
    """
    Saves the standard JSON output to a local directory for dashboard integration.
    """
    base_dir = r"c:\Advanced-Cybersecurity-Intelligence-Platform-Devsecops\modules\soc_defense\outputs"
    
    # Create directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{component_name}_{timestamp}.json"
    file_path = os.path.join(base_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return file_path
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None
