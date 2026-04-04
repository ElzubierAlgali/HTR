import gradio as gr
import os
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, AutoImageProcessor
import base64
import evaluate
import logging

# Only show log messages that are at the ERROR level or above
logging.getLogger('transformers').setLevel(logging.ERROR)

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
image_processor = AutoImageProcessor.from_pretrained("pstroe/bullinger-general-model")
model = VisionEncoderDecoderModel.from_pretrained("pstroe/bullinger-general-model")

# Create examples
def get_example_data(folder_path="./examples/"):
    example_data = []
    all_files = os.listdir(folder_path)
    
    for file_name in all_files:
        file_path = os.path.join(folder_path, file_name)
        
        if file_name.endswith(".png"):
            corresponding_text_file_name = file_name.replace(".png", ".txt")
            corresponding_text_file_path = os.path.join(folder_path, corresponding_text_file_name)
            transcription = "Transcription not found."
            
            try:
                with open(corresponding_text_file_path, "r") as f:
                    transcription = f.read().strip()
            except FileNotFoundError:
                pass
            
            example_data.append([file_path, transcription])
            
    return example_data

def process_image(image, ground_truth):
    cer = None
    
    # Prepare image
    pixel_values = image_processor(image, return_tensors="pt").pixel_values
    
    # Generate (no beam search)
    generated_ids = model.generate(pixel_values)
    
    # Decode
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    if ground_truth is not None and ground_truth.strip() != "":
        cer = cer_metric.compute(predictions=[generated_text], references=[ground_truth])
    else:
        cer = "Ground truth not provided"
    
    return generated_text, cer

# Encode logos
with open("assets/uzh_logo_mod.png", "rb") as img_file:
    logo_html = base64.b64encode(img_file.read()).decode('utf-8')

with open("assets/bullinger_logo.png", "rb") as img_file:
    footer_html = base64.b64encode(img_file.read()).decode('utf-8')

examples = get_example_data()
cer_metric = evaluate.load("cer")

# Custom CSS for enhanced UI
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --primary-color: #1a365d;
    --secondary-color: #c53030;
    --accent-color: #d69e2e;
    --bg-dark: #0f172a;
    --bg-light: #f8fafc;
    --bg-card-dark: #1e293b;
    --bg-card-light: #ffffff;
    --bg-card-hover-dark: #334155;
    --bg-card-hover-light: #f1f5f9;
    --text-primary-dark: #f1f5f9;
    --text-primary-light: #1e293b;
    --text-secondary-dark: #94a3b8;
    --text-secondary-light: #64748b;
    --border-color-dark: #334155;
    --border-color-light: #e2e8f0;
    --success-color: #22c55e;
    --gradient-1: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
    --gradient-2: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%);
    
    /* Default to light theme */
    --bg-main: var(--bg-light);
    --bg-card: var(--bg-card-light);
    --bg-card-hover: var(--bg-card-hover-light);
    --text-primary: var(--text-primary-light);
    --text-secondary: var(--text-secondary-light);
    --border-color: var(--border-color-light);
}

/* Main container styling */
.gradio-container {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg-main) !important;
    min-height: 100vh;
    color: var(--text-primary) !important;
}

/* Custom background pattern - Light theme */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 80%, rgba(26, 54, 93, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(197, 48, 48, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(214, 158, 46, 0.04) 0%, transparent 30%);
    pointer-events: none;
    z-index: 0;
}

.main {
    position: relative;
    z-index: 1;
}

/* Header styling */
.header-container {
    background: linear-gradient(180deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.9) 100%);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-color);
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 12px;
}

.logo-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.logo-section img {
    height: 70px;
    filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
    transition: transform 0.3s ease;
}

.logo-section img:hover {
    transform: scale(1.05);
}

/* Title styling */
.title-main {
    font-family: 'Crimson Pro', serif !important;
    font-size: 2.75rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 50%, #d69e2e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin: 0;
    padding: 0.5rem 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
    animation: fadeInUp 0.8s ease-out;
}

.subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.1rem;
    color: var(--text-secondary);
    text-align: center;
    margin-top: 0.75rem;
    animation: fadeInUp 0.8s ease-out 0.1s both;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Description card */
.description-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    animation: fadeInUp 0.8s ease-out 0.2s both;
}

.description-card p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.7;
    margin: 0;
}

.description-card a {
    color: var(--accent-color);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease;
}

.description-card a:hover {
    color: #eab308;
    text-decoration: underline;
}

/* Feature badges */
.feature-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
    animation: fadeInUp 0.8s ease-out 0.3s both;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    transition: all 0.3s ease;
}

.badge:hover {
    border-color: var(--accent-color);
    color: var(--text-primary);
    transform: translateY(-2px);
}

.badge-icon {
    font-size: 1.1rem;
}

/* Panel styling */
.panel {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: all 0.3s ease !important;
}

.panel:hover {
    border-color: rgba(214, 158, 46, 0.3) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

/* Input/Output labels */
label {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    font-size: 0.9rem !important;
    margin-bottom: 0.5rem !important;
}

/* Image upload area */
.image-container {
    border: 2px dashed var(--border-color) !important;
    border-radius: 12px !important;
    background: rgba(248, 250, 252, 0.8) !important;
    transition: all 0.3s ease !important;
}

.image-container:hover {
    border-color: var(--accent-color) !important;
    background: rgba(248, 250, 252, 1) !important;
}

/* Textboxes */
textarea, input[type="text"] {
    font-family: 'Crimson Pro', serif !important;
    font-size: 1.1rem !important;
    background: rgba(248, 250, 252, 0.9) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 1rem !important;
    transition: all 0.3s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 3px rgba(214, 158, 46, 0.2) !important;
    outline: none !important;
}

textarea::placeholder, input[type="text"]::placeholder {
    color: var(--text-secondary) !important;
    font-style: italic;
}

/* Buttons */
button.primary {
    background: var(--gradient-2) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.875rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: white !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(197, 48, 48, 0.4) !important;
}

button.primary:active {
    transform: translateY(0) !important;
}

button.secondary {
    background: transparent !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

button.secondary:hover {
    border-color: var(--text-primary) !important;
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

/* Section headers */
.section-header {
    font-family: 'Crimson Pro', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-header::before {
    content: '';
    width: 4px;
    height: 24px;
    background: var(--gradient-2);
    border-radius: 2px;
}

/* Examples section */
.examples-section {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 2rem;
}

.gallery {
    border-radius: 12px !important;
    overflow: hidden;
}

/* CER output special styling */
.cer-output {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 0 1rem 0;
    color: var(--text-secondary);
    font-size: 0.85rem;
    border-top: 1px solid var(--border-color);
    margin-top: 3rem;
}

.footer a {
    color: var(--accent-color);
    text-decoration: none;
}

/* How it works section */
.how-it-works {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.step-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.3s ease;
}

.step-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent-color);
}

.step-number {
    width: 40px;
    height: 40px;
    background: var(--gradient-2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: white;
    margin: 0 auto 1rem auto;
    font-size: 1.1rem;
}

.step-title {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.step-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-light);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .title-main {
        font-size: 1.75rem !important;
    }
    
    .logo-section img {
        height: 50px;
    }
    
    .feature-badges {
        gap: 0.5rem;
    }
    
    .badge {
        padding: 0.4rem 0.8rem;
        font-size: 0.75rem;
    }
}

/* Theme switching based on system preference */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: var(--bg-dark);
        --bg-card: var(--bg-card-dark);
        --bg-card-hover: var(--bg-card-hover-dark);
        --text-primary: var(--text-primary-dark);
        --text-secondary: var(--text-secondary-dark);
        --border-color: var(--border-color-dark);
    }
    
    /* Custom background pattern - Dark theme */
    .gradio-container::before {
        background: 
            radial-gradient(circle at 20% 80%, rgba(26, 54, 93, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(197, 48, 48, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(214, 158, 46, 0.1) 0%, transparent 30%) !important;
    }
    
    /* Dark theme overrides */
    .image-container {
        background: rgba(30, 41, 59, 0.5) !important;
    }
    
    .image-container:hover {
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    textarea, input[type="text"] {
        background: rgba(15, 23, 42, 0.6) !important;
    }
    
    .header-container {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark) !important;
    }
}
"""

# Custom theme for Gradio 6.x
custom_theme = gr.themes.Base(
    primary_hue="red",
    secondary_hue="amber",
    neutral_hue="slate",
).set(
    body_background_fill="transparent",
    body_background_fill_dark="transparent",
    block_background_fill="transparent",
    block_background_fill_dark="transparent",
    input_background_fill="transparent",
    input_background_fill_dark="transparent",
    button_primary_background_fill="#c53030",
    button_primary_background_fill_hover="#9b2c2c",
)

# Build the Gradio interface
with gr.Blocks(title="HTR Transformer - Handwritten Text Recognition") as demo:
    
    # Header section with logos
    gr.HTML(f"""
        <div class="header-container">
            <div class="logo-section">
                <img src='data:image/png;base64,{logo_html}' alt="University Logo">
                <img src='data:image/png;base64,{footer_html}' alt="Project Logo">
            </div>
            <h1 class="title-main">✨ Handwritten Text Recognition</h1>
            <p class="subtitle">Powered by Transformer Models & Large Language Models</p>
        </div>
    """)
    
    # Feature badges
    gr.HTML("""
        <div class="feature-badges">
            <span class="badge"><span class="badge-icon">🔬</span> TrOCR Architecture</span>
            <span class="badge"><span class="badge-icon">📜</span> Historical Documents</span>
            <span class="badge"><span class="badge-icon">🎯</span> High Accuracy</span>
            <span class="badge"><span class="badge-icon">⚡</span> Real-time Processing</span>
        </div>
    """)
    
    # Description card
    gr.HTML("""
        <div class="description-card">
            <p>
                This application leverages <strong>Microsoft's TrOCR</strong> — a state-of-the-art encoder-decoder model 
                combining an <em>image Transformer encoder</em> with a <em>text Transformer decoder</em> for exceptional 
                optical character recognition (OCR) and handwritten text recognition (HTR). 
                The model has been fine-tuned on the <a href="https://github.com/pstroe/bullinger-htr" target="_blank">Bullinger Dataset</a> 
                as part of the <a href="https://www.bullinger-digital.ch" target="_blank">Bullinger Digital</a> project, 
                enabling accurate transcription of historical handwritten documents.
            </p>
        </div>
    """)
    
    # How it works section
    gr.HTML("""
        <div class="how-it-works">
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-title">Upload Image</div>
                <div class="step-desc">Select or drag a handwritten text line image</div>
            </div>
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-title">Process</div>
                <div class="step-desc">Transformer analyzes the handwriting patterns</div>
            </div>
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">Transcribe</div>
                <div class="step-desc">Get accurate text transcription instantly</div>
            </div>
            <div class="step-card">
                <div class="step-number">4</div>
                <div class="step-title">Evaluate</div>
                <div class="step-desc">Compare with ground truth using CER metric</div>
            </div>
        </div>
    """)
    
    # Main content area
    with gr.Row(equal_height=True):
        # Input column
        with gr.Column(scale=1):
            gr.HTML('<div class="section-header">Input</div>')
            input_image = gr.Image(
                type="pil", 
                label="📷 Upload Handwritten Text Image",
                elem_classes=["image-container"]
            )
            
            with gr.Row():
                btn_clear = gr.Button(
                    "🗑️ Clear", 
                    variant="secondary",
                    elem_classes=["secondary"]
                )
                btn_submit = gr.Button(
                    "🚀 Recognize Text", 
                    variant="primary",
                    elem_classes=["primary"]
                )
        
        # Output column
        with gr.Column(scale=1):
            gr.HTML('<div class="section-header">Results</div>')
            output_text = gr.Textbox(
                label="📝 Recognized Text",
                placeholder="Transcription will appear here...",
                lines=3,
                interactive=False
            )
            ground_truth = gr.Textbox(
                label="📋 Ground Truth (Optional)",
                placeholder="Enter the actual text to calculate Character Error Rate...",
                lines=2
            )
            cer_output = gr.Textbox(
                label="📊 Character Error Rate (CER)",
                placeholder="CER score will appear here...",
                lines=1,
                interactive=False,
                elem_classes=["cer-output"]
            )
    
    # Examples section
    gr.HTML('<div class="section-header" style="margin-top: 2rem;">Sample Images</div>')
    
    with gr.Accordion("📚 Click to view example images from test set", open=False):
        gr.Examples(
            examples=examples,
            inputs=[input_image, ground_truth],
            label=None,
            examples_per_page=4
        )
    
    # Footer
    gr.HTML("""
        <div class="footer">
            <p>
                <strong>Enhancing Handwritten Text Recognition Using Transformer Models</strong><br>
                Built with 🤗 Transformers & Gradio | 
                <a href="https://huggingface.co/pstroe/bullinger-general-model" target="_blank">Model Card</a> | 
                <a href="https://doi.org/10.5167/uzh-234886" target="_blank">Research Paper</a>
            </p>
        </div>
    """)
    
    # Event handlers
    btn_submit.click(
        process_image, 
        inputs=[input_image, ground_truth], 
        outputs=[output_text, cer_output]
    )
    
    btn_clear.click(
        lambda: [None, "", "", ""], 
        outputs=[input_image, output_text, ground_truth, cer_output]
    )

if __name__ == "__main__":
    demo.launch(
        favicon_path="assets/bullinger_logo.png",
        share=False,
        theme=custom_theme,
        css=custom_css
    )
