# Fixflow


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

**Terminal 1:**

Start the uvicorn server to run the Fixflow API server from the `api-server` directory:

```bash
source venv/bin/activate
uvicorn shortcuts:app --reload --host 127.0.0.1 --port 8000
```

This command will start the server in development mode with hot reloading, listening on localhost port 8000.

**Terminal 2:**

In a separate terminal window, navigate to the `api-server` directory again:

```bash
source venv/bin/activate
cd fixflow/api-server
```

Run the application using the following command:

```bash
python app.py
```

Open VSCode, install the `fixflow/fixflow-extension/fixflow-0.0.1.vsix` vscode extension to communicate with the above 2 servers.