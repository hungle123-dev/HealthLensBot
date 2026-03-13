"""
CrewAI tool functions for HealthLensBot.
Each @tool function is a standalone module-level function (no class wrappers needed).
"""

import os
import base64
import requests
import logging
import json
import re
from io import BytesIO
from typing import List, Optional

from crewai.tools import tool
from src.config import client, VISION_MODEL, TEXT_MODEL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _load_image_as_base64(image_input: str) -> str:
    """
    Load an image from a local path or URL and return its base64-encoded string.

    :param image_input: The image file path (local) or URL (remote).
    :return: Base64-encoded string of the image.
    :raises FileNotFoundError: If the local file does not exist.
    """
    if image_input.startswith("http"):
        response = requests.get(image_input)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
    else:
        if not os.path.isfile(image_input):
            raise FileNotFoundError(f"No file found at path: {image_input}")
        with open(image_input, "rb") as file:
            image_bytes = BytesIO(file.read())

    return base64.b64encode(image_bytes.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool("Extract ingredients")
def extract_ingredients(image_input: str) -> str:
    """
    Extract ingredients from a food item image.

    :param image_input: The image file path (local) or URL (remote).
    :return: A list of ingredients extracted from the image.
    """
    logger.info("Extracting ingredients from image: %s", image_input)
    encoded_image = _load_image_as_base64(image_input)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract ingredients from the food item image"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            }
        ],
    )

    return response.choices[0].message.content


@tool("Filter ingredients")
def filter_ingredients(raw_ingredients: str) -> List[str]:
    """
    Processes the raw ingredient data and filters out non-food items or noise.

    :param raw_ingredients: Raw ingredients as a string.
    :return: A list of cleaned and relevant ingredients.
    """
    ingredients = [
        ingredient.strip().lower()
        for ingredient in raw_ingredients.split(",")
        if ingredient.strip()
    ]
    return ingredients




@tool("Filter based on dietary restrictions")
def filter_based_on_restrictions(
    ingredients: List[str],
    dietary_restrictions: Optional[str] = None,
) -> List[str]:
    """
    Uses an LLM model to filter ingredients based on dietary restrictions.

    :param ingredients: List of ingredients.
    :param dietary_restrictions: Dietary restrictions (e.g., vegan, gluten-free). Defaults to None.
    :return: Filtered list of ingredients that comply with the dietary restrictions.
    """
    if not dietary_restrictions:
        return ingredients

    prompt = (
        f"You are an AI nutritionist specialized in dietary restrictions. "
        f"Given the following list of ingredients: {', '.join(ingredients)}, "
        f"and the dietary restriction: {dietary_restrictions}, "
        f"remove any ingredient that does not comply with this restriction. "
        f"Respond ONLY with a JSON array of strings containing the compliant ingredients. "
        f"Do not include any other text or markdown formatting. Example: [\"apple\", \"banana\"]"
    )

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            response_format={"type": "json_object"} if "llama" not in TEXT_MODEL.lower() else None # OpenRouter Llama might reject json_object if not explicitly supported
        )

        content = response.choices[0].message.content.strip()
        
        # Robust parsing: try to find an array in the string if it's wrapped in markdown
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            filtered_list = json.loads(json_str)
            if isinstance(filtered_list, list):
                return [str(item).strip().lower() for item in filtered_list if str(item).strip()]
                
        # Fallback if regex fails but response is comma separated anyway
        return [item.strip().lower() for item in content.replace('[', '').replace(']', '').replace('"', '').replace("'", '').split(",") if item.strip()]

    except Exception as e:
        logger.error(f"Error filtering ingredients: {e}")
        return ingredients # Fallback to original ingredients if LLM fails


@tool("Analyze nutritional values and calories of the dish from uploaded image")
def analyze_image(image_input: str) -> str:
    """
    Provide a detailed nutrient breakdown and estimate the total calories
    of all ingredients from the uploaded image.

    :param image_input: The image file path (local) or URL (remote).
    :return: A string with nutrient breakdown and estimated calorie information.
    """
    logger.info("Analyzing nutritional content from image: %s", image_input)
    encoded_image = _load_image_as_base64(image_input)

    assistant_prompt = """\
You are an expert nutritionist. Analyze the food items in the image and provide:
1. **Identification**: List each identified food item clearly, one per line.
2. **Portion Size & Calorie Estimation**: For each item, specify the portion size and estimated calories.
   - **[Food Item]**: [Portion Size], [Number of Calories] calories
3. **Total Calories**: Provide the total number of calories for all food items.
4. **Nutrient Breakdown**: Include a breakdown of **Protein**, **Carbohydrates**, **Fats**, **Vitamins**, and **Minerals**.
5. **Health Evaluation**: Evaluate the healthiness of the meal in one paragraph.
6. **Disclaimer**: Include the following exact text:
   The nutritional information and calorie estimates provided are approximate and are based on general food data.
   Actual values may vary depending on factors such as portion size, specific ingredients, preparation methods, and individual variations.
   For precise dietary advice or medical guidance, consult a qualified nutritionist or healthcare provider.
Format your response exactly like the template above to ensure consistency."""

    response = client.chat.completions.create(
        model=VISION_MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": assistant_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            }
        ],
    )

    return response.choices[0].message.content
