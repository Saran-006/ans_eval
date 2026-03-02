from doctr.io import DocumentFile
from doctr.models import ocr_predictor

doc = DocumentFile.from_images("../samples/img5.jpeg")
model = ocr_predictor(pretrained=True)

result = model(doc)

print(result.render())