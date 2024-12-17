import subprocess

def get_vscode_windows():
    """
    Get all open VSCode windows and their titles on MacOS using AppleScript.
    Returns a list of window titles.
    """
    applescript = '''
    tell application "Visual Studio Code"
        if it is running then
            set windowList to {}
            tell application "System Events"
                tell process "Code"
                    set windowList to name of every window
                end tell
            end tell
            return windowList
        end if
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            window_titles = result.stdout.strip().split(', ')
            return [title.strip() for title in window_titles if title.strip()]
        else:
            print(f"Error: {result.stderr if result.stderr else 'No windows found'}")
            return []
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def switch_to_window(window_name):
    """
    Switch to a specific VSCode window by its name.
    Args:
        window_name (str): The title of the window to switch to
    Returns:
        bool: True if successful, False otherwise
    """
    applescript = f'''
    tell application "Visual Studio Code"
        activate
        tell application "System Events"
            tell process "Code"
                set targetWindow to null
                repeat with w in windows
                    if name of w contains "{window_name}" then
                        set targetWindow to w
                        exit repeat
                    end if
                end repeat
                if targetWindow is not null then
                    set frontmost to true
                    perform action "AXRaise" of targetWindow
                    return true
                end if
            end tell
        end tell
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error switching to window: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    windows = get_vscode_windows()
    
    if windows:
        print("Open VSCode windows:")
        for i, title in enumerate(windows, 1):
            print(f"{i}. {title}")
            
        # Example: Switch to the first window
        if windows:
            target_window = windows[1]
            print(f"\nTrying to switch to window: {target_window}")
            if switch_to_window(target_window):
                print("Successfully switched windows")
            else:
                print("Failed to switch windows")
    else:
        print("No VSCode windows found or VSCode is not running")