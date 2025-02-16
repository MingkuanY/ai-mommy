import screen_brightness_control as sbc

def set_brightness(value):
    """
    Set the display brightness using screen_brightness_control.
    
    Args:
        value (float): Brightness value between 0.0 and 1.0
    """
    if not 0.0 <= value <= 1.0:
        raise ValueError("Brightness must be between 0.0 and 1.0")
    
    # Convert to percentage (0-100)
    brightness_percent = int(value * 100)
    
    try:
        # Set brightness for all displays
        sbc.set_brightness(brightness_percent)
    except Exception as e:
        print(f"Error setting brightness: {e}")

def get_brightness():
    """Get current brightness level."""
    try:
        # Get brightness of primary display
        return sbc.get_brightness()[0] / 100.0
    except Exception as e:
        print(f"Error getting brightness: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Print current brightness
    print(f"Current brightness: {get_brightness()}")
    
    # Set brightness to 80%
    set_brightness(0.8)