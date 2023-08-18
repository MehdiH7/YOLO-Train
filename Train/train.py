#Multi-GPU Training on YOLO

import time
import logging
import psutil
import GPUtil
from tqdm import tqdm
from ultralytics import YOLO
import comet_ml
import torch
import utils

# Initialize Logging
logging.basicConfig(filename='training_log.log', level=logging.INFO)

comet_ml.init(project_name='YOLOV8_Soccer')
display = utils.notebook_init()

# Combine model paths and load flags into a single dictionary
models_to_load = {
    'yolov8n': {'path': 'yolov8n.pt', 'load': True},   # nano - 3.2 Million parameters
    'YOLOv8s': {'path': 'yolov8s.pt', 'load': False},  # small - 11.2 million parameters
    'YOLOv8m': {'path': 'yolov8m.pt', 'load': False},  # medium - 25.9 million parameters
    'YOLOv8l': {'path': 'yolov8l.pt', 'load': False},  # large - 43.7 million parameters
    'YOLOv8x': {'path': 'yolov8x.pt', 'load': False},  # Xlarge - 68.2 million parameters
}

# Find the model to load
selected_model_path = next((model['path'] for model in models_to_load.values() if model['load']), None)

# Check if a model was found
if selected_model_path:
    logging.info(f"Loading model from: {selected_model_path}")
    print(f"Loading model from: {selected_model_path}")
    model = YOLO(selected_model_path)

    start_time = time.time()

    for epoch in tqdm(range(100), desc="Training progress"):  # using tqdm for progress bar
        # Check CPU and GPU usage
        cpu_usage = psutil.cpu_percent()
        gpu_usage = GPUtil.getGPUs()[0].load
        logging.info(f"Epoch {epoch + 1}: CPU Usage: {cpu_usage}%, GPU Usage: {gpu_usage}%")

        # Train the model with 2 GPUs
        results = model.train(
            data = 'config.yaml',
            project = 'YOLOV8_Soccer', #Project name
            device = [0, 1],        #device to run on, i.e. cuda device=0 or device=0,1,2,3 or device=cpu
            bbox_interval = 1       #log model predictions and the associated images by passing the bbox_interval command line argument. Predictions can be visualized using Comet's Object Detection Custom Panel
            
            #Model Hyperparameters
            epochs = 100, 
            imgsz = 640, 
            device = [0, 1],        #device to run on, i.e. cuda device=0 or device=0,1,2,3 or device=cpu
            patience = 50,
            batch = 16,
            save = True,
            save_period = 5,
            workers = 8,
            pretrained = True,
            optimizer = 'AdamW',    #choices=[SGD, Adam, Adamax, AdamW, NAdam, RAdam, RMSProp, auto]
            verbose = True,
            seed = 7,
            cos_lr = True,          #use cosine learning rate scheduler
            resume = True,
            freeze = 1,             #(int or list, optional) freeze first n layers, or freeze list of layer indices during training
            lr0 = 0.01,             #initial learning rate (i.e. SGD=1E-2, Adam=1E-3)
            warmup_epochs = 3.0,
            dropout = 0.5
            )
    
    end_time = time.time()
    execution_time_minutes = (end_time - start_time) / 60
    logging.info(f"Training completed in {execution_time_minutes:.2f} minutes.")

else:
    print("No model selected!")






