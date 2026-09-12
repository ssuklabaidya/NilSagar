from ultralytics import YOLO

def main():
    model = YOLO("yolov8n-cls.pt")
    results = model.train(
        data="datasets/classify",
        epochs=30,
        imgsz=224,
        device=0,
        project="runs_classify",
        name="nilsagar_v1",
    )

if __name__ == "__main__":
    main()