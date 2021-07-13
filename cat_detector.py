import torch
from torchvision import transforms
import pickle
from PIL import Image


class CatDetector:
    def __init__(self, model_file: str):
        self.model = pickle.load(open(model_file, 'rb'))
        self.model.eval()

    def isCatFile(self, image_file: str):
        image = Image.open(image_file)
        return self.isCatImage(image)

    def isCatImage(self, image):
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        batch = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = self.model(batch)

        return bool(output[0, 0] > output[0, 1])


if __name__ == '__main__':
    cd = CatDetector('CatNet13-07-2021-1050')
    print(cd.isCatFile('./data/val/others/n01440764_6206.JPEG'))
