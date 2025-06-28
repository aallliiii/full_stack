#!/usr/bin/env python
import sys
import warnings
import gradio as gr
from datetime import datetime
from crew import FullStack

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from dotenv import load_dotenv
load_dotenv()

def run_full_stack(requirements, module_name, class_name):
    """
    Run the research crew with the provided inputs and return the result.
    """
    inputs = {
        'requirements': requirements,
        'module_name': module_name,
        'class_name': class_name
    }
    
    try:
        result = FullStack().crew().kickoff(inputs=inputs)
        return result.raw
    except Exception as e:
        return f"An error occurred: {str(e)}"

def create_interface():
    """
    Create and launch the Gradio interface.
    """
    default_requirements = """"""

    with gr.Blocks(title="Full Stack System Generator") as interface:
        gr.Markdown("# Full Stack System Generator")
        gr.Markdown("Enter your requirements and settings to generate the system code.")
        
        with gr.Row():
            with gr.Column():
                requirements = gr.Textbox(
                    label="System Requirements",
                    value=default_requirements,
                    lines=20,
                    max_lines=50,
                    interactive=True
                )
                
                with gr.Row():
                    module_name = gr.Textbox(
                        label="Module Name",
                        value="",
                        interactive=True
                    )
                    class_name = gr.Textbox(
                        label="Class Name",
                        value="",
                        interactive=True
                    )
                
                submit_btn = gr.Button("Generate System", variant="primary")
            
            with gr.Column():
                output = gr.Textbox(
                    label="Generated Output",
                    lines=20,
                    max_lines=50,
                    interactive=False
                )
        
        submit_btn.click(
            fn=run_full_stack,
            inputs=[requirements, module_name, class_name],
            outputs=output
        )
        
        
    return interface

if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)