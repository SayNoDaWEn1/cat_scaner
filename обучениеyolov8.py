from ultralytics import YOLO

if __name__ == '__main__':
    # Загрузка предобученной модели YOLOv8
    model = YOLO('yolov8n.pt')  # Используйте YOLOv8 Nano для быстрого обучения

    # Запуск обучения
    model.train(data='D:/PythonProject/dataset2.0/data.yaml', epochs=50, imgsz=640)
