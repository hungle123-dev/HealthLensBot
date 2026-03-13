"""
HealthLensBot — Gradio UI entry point.
"""

# Import config FIRST to ensure env vars are set before CrewAI loads
import src.config  # noqa: F401  (side-effect import)

import gradio as gr
import tempfile
import uuid
import os

from src.crew import HealthLensBotRecipeCrew, HealthLensBotAnalysisCrew
from src.formatters import format_recipe_output, format_analysis_output


# ---------------------------------------------------------------------------
# Core workflow function
# ---------------------------------------------------------------------------

def analyze_food(image, dietary_restrictions, workflow_type, progress=gr.Progress(track_tqdm=True)):
    """
    Wrapper function for the Gradio interface.

    :param image: Uploaded image (PIL format)
    :param dietary_restrictions: Dietary restriction as a string (e.g., "vegan")
    :param workflow_type: Workflow type ("recipe" or "analysis")
    :return: Result from the HealthLensBot workflow.
    """
    if image is None:
        return "Please upload an image first."

    # Create a unique temporary file
    temp_dir = tempfile.gettempdir()
    unique_filename = f"healthlensbot_upload_{uuid.uuid4().hex}.jpg"
    image_path = os.path.join(temp_dir, unique_filename)

    try:
        image.save(image_path)

        inputs = {
            "uploaded_image": image_path,
            "dietary_restrictions": dietary_restrictions,
            "workflow_type": workflow_type,
        }

        # Initialize the appropriate crew instance based on workflow type
        if workflow_type == "recipe":
            crew_instance = HealthLensBotRecipeCrew(
                image_data=image_path,
                dietary_restrictions=dietary_restrictions,
            )
        elif workflow_type == "analysis":
            crew_instance = HealthLensBotAnalysisCrew(image_data=image_path)
        else:
            return "Invalid workflow type. Choose 'recipe' or 'analysis'."

        # Run the crew workflow and get the result
        crew_obj = crew_instance.crew()
        final_output = crew_obj.kickoff(inputs=inputs).to_dict()

        if workflow_type == "recipe":
            return format_recipe_output(final_output)
        elif workflow_type == "analysis":
            return format_analysis_output(final_output)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"## ❌ Error Processing Request\n\nAn error occurred while analyzing the image. Please try again later.\n\n**Details for developer:**\n```\n{e}\n```"
    finally:
        # Clean up the temporary file
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

css = """
.title {
    font-size: 1.5em !important;
    text-align: center !important;
    color: #FFD700;
}
.text {
    text-align: center;
}
"""

js = """
function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginBottom = '20px';
    container.style.color = '#eba93f';

    var text = 'Welcome to your AI HealthLensBot!';
    for (var i = 0; i < text.length; i++) {
        (function(i){
            setTimeout(function(){
                var letter = document.createElement('span');
                letter.style.opacity = '0';
                letter.style.transition = 'opacity 0.1s';
                letter.innerText = text[i];

                container.appendChild(letter);

                setTimeout(function() {
                    letter.style.opacity = '0.9';
                }, 50);
            }, i * 250);
        })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);

    return 'Animation created';
}
"""


with gr.Blocks(title="HealthLensBot") as demo:
    gr.Markdown("# How it works", elem_classes="title")
    gr.Markdown(
        "Upload an image of your fridge content, enter your dietary restriction "
        "(if you have any!) and select a workflow type 'recipe' then click "
        "'Analyze' to get recipe ideas.",
        elem_classes="text",
    )
    gr.Markdown(
        "Upload an image of a complete dish, leave dietary restriction blank "
        "and select a workflow type 'analysis' then click 'Analyze' to get "
        "nutritional insights.",
        elem_classes="text",
    )
    gr.Markdown(
        "You can also select one of the examples provided to autofill the "
        "input sections and click 'Analyze' right away!",
        elem_classes="text",
    )

    with gr.Row():
        with gr.Column(scale=1, min_width=400):
            gr.Markdown("## Inputs", elem_classes="title")
            image_input = gr.Image(type="pil", label="Upload Image")
            dietary_input = gr.Textbox(
                label="Dietary Restrictions (optional)",
                placeholder="e.g., vegan",
            )
            workflow_radio = gr.Radio(["recipe", "analysis"], label="Workflow Type")
            submit_btn = gr.Button("Analyze")

        with gr.Column(scale=2, min_width=600):
            gr.Examples(
                examples=[
                    ["examples/food-1.jpg", "vegan", "recipe"],
                    ["examples/food-2.jpg", "", "analysis"],
                    ["examples/food-3.jpg", "keto", "recipe"],
                    ["examples/food-4.jpg", "", "analysis"],
                ],
                inputs=[image_input, dietary_input, workflow_radio],
                label="Try an Example: Select one of the examples below to autofill the input section then click Analyze",
            )
            
            gr.Markdown("## Results will appear here...", elem_classes="title")
            result_display = gr.Markdown(
                "<div style='border: 1px solid #ccc; "
                "padding: 1rem; text-align: center; "
                "color: #666;'>No results yet</div>",
                height=500,
            )

    # Disable button during processing
    submit_btn.click(
        fn=lambda: gr.update(interactive=False, value="Processing..."),
        inputs=None,
        outputs=submit_btn,
    ).then(
        fn=analyze_food,
        inputs=[image_input, dietary_input, workflow_radio],
        outputs=result_display,
    ).then(
        fn=lambda: gr.update(interactive=True, value="Analyze"),
        inputs=None,
        outputs=submit_btn,
    )

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=5000,
        theme=gr.themes.Citrus(),
        css=css,
        js=js,
    )
