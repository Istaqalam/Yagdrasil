from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Crop Recognition API"}


# Load the model
MODEL_PATH = "../../Models/1"
MODEL = tf.keras.models.load_model(MODEL_PATH)

# Class names
CLASS_NAMES = ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]


@app.get("/ping")
async def ping():
    return "Server is working and alive"


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))

    return image


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image = read_file_as_image(await file.read())
        img_batch = np.expand_dims(image, 0)

        predictions = MODEL.predict(img_batch)

        predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
        confidence = float(np.max(predictions[0]))

        return {
            'class': predicted_class,
            'confidence': confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)

