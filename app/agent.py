# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.external_recipe_tool import search_online_recipes
from app.firestore_tools import add_recipe, get_recipe, search_recipes
from app.image_tool import generate_dish_image
from app.maps_tools import find_nearby_places, geocode_address
from app.scaling_tool import calculate_recipe_scaling

# Load Agent Engine Sandbox Code Executor from deployment_metadata.json if available
_metadata_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "deployment_metadata.json"
)
code_executor = None
if os.path.exists(_metadata_path):
    try:
        with open(_metadata_path, "r") as _f:
            _meta = json.load(_f)
        _sandbox_name = _meta.get("sandbox_resource_name") or _meta.get(
            "sandbox_environment_id"
        )
        _agent_engine_name = _meta.get("remote_agent_runtime_id")
        if _sandbox_name:
            code_executor = AgentEngineSandboxCodeExecutor(
                sandbox_resource_name=_sandbox_name
            )
        elif _agent_engine_name:
            code_executor = AgentEngineSandboxCodeExecutor(
                agent_engine_resource_name=_agent_engine_name
            )
    except Exception:
        pass


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        # Gracefully handle when memory service is not configured
        pass
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Recipe Chef, an AI culinary assistant that helps home cooks explore, "
        "search, and save delicious recipes. "
        "IMPORTANT: You remember and recall all user food allergies, dietary restrictions, "
        "and health preferences across conversations. Whenever a user mentions any allergy "
        "(e.g., peanuts, gluten, dairy, shellfish, eggs, tree nuts, soy) or dietary restriction "
        "(e.g., vegan, vegetarian, halal, kosher), remember it and strictly filter out any "
        "recipes or ingredients that contain those allergens in all future turns and sessions. "
        "You have access to a local Firestore database containing curated recipes, a global "
        "public recipe API (TheMealDB), Google Geocoding API, Google Places API (New), and "
        "a Python code execution sandbox. "
        "Use `search_recipes` for local Firestore recipes, `search_online_recipes` to search "
        "the global external database for recipes online, `get_recipe` to view full cooking instructions, "
        "`add_recipe` to save new recipes, `calculate_recipe_scaling` to scale ingredients for "
        "serving sizes, `geocode_address` to convert an address into coordinates, `find_nearby_places` "
        "to find nearby grocery stores or restaurants, `generate_dish_image` to generate a visual photo "
        "hosted publicly on Cloud Storage, and write Python code when custom complex calculations or code execution is required."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        search_recipes,
        search_online_recipes,
        get_recipe,
        add_recipe,
        calculate_recipe_scaling,
        geocode_address,
        find_nearby_places,
        generate_dish_image,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
