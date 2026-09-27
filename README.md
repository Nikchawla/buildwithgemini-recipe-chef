# Recipe Chef 👨‍🍳

**Recipe Chef** is an AI-powered conversational culinary assistant built with Google's Agent Development Kit (ADK) and Gemini 2.5. It helps home cooks explore recipes, manage food allergies across sessions, scale ingredient portions in a secure Python sandbox, generate dish images, find nearby grocery stores, and render rich interactive UI cards via A2UI.

---

## 🌟 Implemented Features & Architecture

### 1. 🧠 Cross-Session Memory (Vertex AI Memory Bank)
- Automatically remembers user dietary restrictions, food allergies (e.g., peanuts, gluten, dairy), and health preferences across conversations.
- Uses ADK's `PreloadMemoryTool` and `add_session_to_memory()` callback to load and save long-term memories in Vertex AI Memory Bank.

### 2. 🗄️ Recipe Database & Storage (Google Cloud Firestore)
- Persists curated recipe catalog with Firestore.
- **Tools**:
  - `search_recipes`: Query recipes by cuisine, ingredients, or title.
  - `get_recipe`: Retrieve detailed step-by-step cooking instructions and ingredients.
  - `add_recipe`: Save custom user recipes into Firestore.

### 3. 🌐 Global Public Recipe Search (TheMealDB API)
- Connects to the public [TheMealDB](https://www.themealdb.com/) API.
- **Tool**: `search_online_recipes` to search external global recipes when not found in the local database.

### 4. 🧮 Secure Python Code Execution (Agent Engine Sandbox)
- Runs ingredient portion scaling and nutritional macro calculations safely inside an `AgentEngineSandboxCodeExecutor` sandbox.
- **Tool**: `calculate_recipe_scaling`.

### 5. 📸 Visual Dish Generation (Google Cloud Storage & Imagen)
- Generates visual dish previews and plating photos, storing the generated assets in a Google Cloud Storage bucket (`recipe-chef-assets-*`).
- **Tool**: `generate_dish_image`.

### 6. 🗺️ Location & Grocery Search (Google Maps Geocoding & Places API)
- Integrates directly with Google Maps Platform REST endpoints to convert addresses and locate food suppliers.
- **Tools**:
  - `geocode_address`: Converts physical addresses into latitude/longitude coordinates.
  - `find_nearby_places`: Finds nearby grocery stores, supermarkets, or culinary markets.

### 7. 🎨 Rich UI Cards (A2UI v0.8)
- Configured with `A2uiSchemaManager` (v0.8) and the Basic Catalog to return structured UI cards.
- Custom `after_model_callback` (`a2ui_callback`) renders rich component cards (Card, Column, Row, Text, Image) dynamically in both `adk web` and the custom web frontend.

### 8. 🌐 Custom Web Frontend & FastAPI A2A Proxy
- Minimal FastAPI proxy server (`frontend/main.py`) translating browser HTTP requests to the deployed agent over the A2A protocol.
- Custom chat UI (`frontend/static/index.html`) styled with warm terracotta culinary branding, pre-configured prompt chips, and a native A2UI renderer.
- Containerized (`frontend/Dockerfile`) for deployment to Google Cloud Run.

---

## 🛠️ Project Structure

```
recipe-chef/
├── app/                        # Agent application source
│   ├── agent.py                # Main ADK agent definition & prompt
│   ├── a2ui_utils.py           # A2UI callback and schema processing
│   ├── firestore_tools.py      # Firestore recipe tools
│   ├── external_recipe_tool.py # TheMealDB public API tool
│   ├── scaling_tool.py         # Recipe scaling calculations
│   ├── image_tool.py           # Image generation & GCS upload tool
│   └── maps_tools.py           # Google Maps Geocoding & Places API tools
├── frontend/                   # Custom web frontend & FastAPI proxy
│   ├── main.py                 # FastAPI proxy server (A2A protocol)
│   ├── Dockerfile              # Cloud Run container definition
│   ├── requirements.txt        # Frontend dependencies
│   └── static/
│       └── index.html          # Plain JS/CSS chat UI with A2UI renderer
├── agents-cli-manifest.yaml    # Agents CLI manifest
└── deployment_metadata.json    # Deployed Agent Engine & Sandbox metadata
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Google Cloud Project with Vertex AI, Firestore, and Maps APIs enabled
- `uv` and `agents-cli` installed

### Environment Setup
Create a `.env` file in the project root:
```bash
GOOGLE_MAPS_API_KEY="<YOUR_MAPS_API_KEY>"
```

### Running the Local Agent Playground
To run the ADK local web playground with Memory Bank support:
```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<YOUR_MEMORY_BANK_ID>
```

### Running the Frontend Proxy Locally
Navigate to the `frontend` directory, set environment variables, and run the FastAPI server:
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
uv run python main.py
```

### Deploying to Google Cloud Run
Deploy the frontend container to Cloud Run:
```bash
cd frontend
gcloud run deploy recipe-chef-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<AGENT_ENGINE_RESOURCE_NAME>",AGENT_DIRECTORY="app"
```
