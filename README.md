# Fixflow

## Demo
<a href="https://odysee.com/@rushi:2/fixflow-demo:0" target="_blank">
  <img src="https://s3.amazonaws.com/cdn.freshdesk.com/data/helpdesk/attachments/production/1079857321/original/5hs--T2zBkdydDD16hRXpMFA5ZIpZ2Zpyg.png?1562585254" alt="Video Thumbnail"> 
</a>

## Getting Started

### Installation

1. Clone the Fixflow repository:

```bash
git clone [https://github.com/0xrushi/fixflow.git](https://github.com/0xrushi/fixflow.git)
```

2. Navigate to the `api-server` directory:

```bash
cd fixflow/api-server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Add your OpenAI API key to the `.env` file. The format should be:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

## Running the application

Start the uvicorn server to run the Fixflow API server from the `api-server` directory:

```bash
source venv/bin/activate
uvicorn shortcuts:app --reload --host 127.0.0.1 --port 8000
```

This command will start the server in development mode with hot reloading, listening on localhost port 8000.

Add the below flow in the shortcuts app:
<img width="1112" alt="Screenshot 2025-01-05 at 10 12 30 AM" src="https://github.com/user-attachments/assets/2d4bdd5b-b461-496f-b057-3a2c5eeddb5d" />


Open VSCode, install the `fixflow/fixflow-extension/fixflow-0.0.1.vsix` vscode extension to communicate with the above api.
