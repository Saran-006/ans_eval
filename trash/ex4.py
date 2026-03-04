from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import torch

model_id = "HuggingFaceM4/idefics2-8b"

print("Loading Idefics2 model... (first time download is large)")

processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForVision2Seq.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    device_map="auto"
)

# Load your handwritten image
image = Image.open("../samples/img6.jpg").convert("RGB")

prompt = """
Read all the handwritten text in this image carefully.
Return the full text exactly as written.
Keep line-by-line formatting.
"""

inputs = processor(
    text=prompt,
    images=image,
    return_tensors="pt"
).to(model.device)

with torch.no_grad():
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=500
    )

output = processor.decode(generated_ids[0], skip_special_tokens=True)

print("\nExtracted Text:\n")
print(output)