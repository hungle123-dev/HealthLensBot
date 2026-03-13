"""
CrewAI agent/task/crew definitions for HealthLensBot.
"""

import os
import yaml
from typing import Optional

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.tools import (
    extract_ingredients,
    filter_ingredients,
    filter_based_on_restrictions,
    analyze_image,
)
from src.models import RecipeSuggestionOutput, NutrientAnalysisOutput

# Absolute path to the config directory
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


# ---------------------------------------------------------------------------
# Base Crew (shared agents, tasks, config loading)
# ---------------------------------------------------------------------------

@CrewBase
class BaseHealthLensBotCrew:
    agents_config_path = os.path.join(CONFIG_DIR, "agents.yaml")
    tasks_config_path = os.path.join(CONFIG_DIR, "tasks.yaml")

    def __init__(self, image_data: str, dietary_restrictions: Optional[str] = None):
        self.image_data = image_data
        self.dietary_restrictions = dietary_restrictions

        with open(self.agents_config_path, "r") as f:
            self.agents_config = yaml.safe_load(f)

        with open(self.tasks_config_path, "r") as f:
            self.tasks_config = yaml.safe_load(f)

    # --- Agents ---

    @agent
    def ingredient_detection_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["ingredient_detection_agent"],
            tools=[extract_ingredients, filter_ingredients],
            allow_delegation=False,
            max_iter=5,
            verbose=True,
        )

    @agent
    def dietary_filtering_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["dietary_filtering_agent"],
            tools=[filter_based_on_restrictions],
            allow_delegation=True,
            max_iter=6,
            verbose=True,
        )

    @agent
    def nutrient_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["nutrient_analysis_agent"],
            tools=[analyze_image],
            allow_delegation=False,
            max_iter=4,
            verbose=True,
        )

    @agent
    def recipe_suggestion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["recipe_suggestion_agent"],
            allow_delegation=False,
            verbose=True,
        )

    # --- Tasks ---

    @task
    def ingredient_detection_task(self) -> Task:
        cfg = self.tasks_config["ingredient_detection_task"]
        return Task(
            description=cfg["description"],
            agent=self.ingredient_detection_agent(),
            expected_output=cfg["expected_output"],
        )

    @task
    def dietary_filtering_task(self) -> Task:
        cfg = self.tasks_config["dietary_filtering_task"]
        return Task(
            description=cfg["description"],
            agent=self.dietary_filtering_agent(),
            depends_on=["ingredient_detection_task"],
            input_data=lambda outputs: {
                "ingredients": outputs["ingredient_detection_task"],
                "dietary_restrictions": self.dietary_restrictions,
            },
            expected_output=cfg["expected_output"],
        )

    @task
    def nutrient_analysis_task(self) -> Task:
        cfg = self.tasks_config["nutrient_analysis_task"]
        return Task(
            description=cfg["description"],
            agent=self.nutrient_analysis_agent(),
            expected_output=cfg["expected_output"],
            output_json=NutrientAnalysisOutput,
        )

    @task
    def recipe_suggestion_task(self) -> Task:
        cfg = self.tasks_config["recipe_suggestion_task"]
        return Task(
            description=cfg["description"],
            agent=self.recipe_suggestion_agent(),
            depends_on=["dietary_filtering_task"],
            input_data=lambda outputs: {
                "filtered_ingredients": outputs["dietary_filtering_task"],
            },
            expected_output=cfg["expected_output"],
            output_json=RecipeSuggestionOutput,
        )


# ---------------------------------------------------------------------------
# Concrete Crews
# ---------------------------------------------------------------------------

@CrewBase
class HealthLensBotRecipeCrew(BaseHealthLensBotCrew):
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.ingredient_detection_agent(),
                self.dietary_filtering_agent(),
                self.recipe_suggestion_agent(),
            ],
            tasks=[
                self.ingredient_detection_task(),
                self.dietary_filtering_task(),
                self.recipe_suggestion_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )


@CrewBase
class HealthLensBotAnalysisCrew(BaseHealthLensBotCrew):
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.nutrient_analysis_agent()],
            tasks=[self.nutrient_analysis_task()],
            process=Process.sequential,
            verbose=True,
        )
