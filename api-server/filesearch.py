import os
from pathlib import Path
from typing import List, Dict
import json
from openai import OpenAI

def get_file_paths(directory: str, extensions: List[str] = ['py', 'yml', 'md']) -> List[str]:
    """
    Returns full paths for all files with specified extensions in a directory and its subdirectories.
    """
    extensions = [f'.{ext.lower().strip(".")}' for ext in extensions]
    file_paths = []
    root_dir = Path(directory)
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in extensions:
                file_paths.append(str(file_path.absolute()))
    
    return file_paths

def find_closest_file(search_term: str, file_paths: List[str], api_key: str) -> Dict:
    """
    Uses GPT-4 to find the file name that most closely matches the search term.
    
    Args:
        search_term (str): The search term to match against
        file_paths (List[str]): List of file paths to search through
        api_key (str): OpenAI API key
    
    Returns:
        Dict: JSON response containing the best match and similarity score
    """
    
    file_names = [Path(path).name for path in file_paths]
    
    system_prompt = """You are a helpful assistant that finds the most semantically similar filename from a list.
    Analyze the conceptual meaning of the search term and find the best matching filename.
    Return only a JSON object with no additional text."""
    
    user_prompt = f"""Given the search term "{search_term}", find the most semantically similar filename from this list:
    {json.dumps(file_names, indent=2)}
    
    Return a JSON object with:
    {{
        "best_match": "filename",
        "similarity_score": 0.XX,
        "explanation": "brief reason for the match"
    }}
    
    The similarity score should be between 0 and 1, where 1 is a perfect match."""
    
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={ "type": "json_object" }
    )
    
    result = json.loads(response.choices[0].message.content)
    
    matched_path = next((path for path in file_paths if Path(path).name == result["best_match"]), None)
    result["full_path"] = matched_path
    
    return result

def llm_file_search(directory: str, search_term: str, api_key: str) -> Dict:
    """
    Main function to find files and match them against the search term.
    
    Args:
        directory (str): Directory to search in
        search_term (str): Term to match against file names
        api_key (str): OpenAI API key
    
    Returns:
        Dict: JSON response with match results
    """
    try:
        # Get all relevant files
        file_paths = get_file_paths(directory)
        
        if not file_paths:
            return {
                "error": "No matching files found in directory",
                "files_searched": 0
            }
        
        result = find_closest_file(search_term, file_paths, api_key)
        result["files_searched"] = len(file_paths)
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "files_searched": 0
        }
        
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")

    directory = "/Users/bread/Documents/vscodeproj/api-server"
    search_term = "app dot buy for server"
    search_term = "open app.pi file"

    result = llm_file_search(directory, search_term, api_key)

    print(json.dumps(result, indent=2))