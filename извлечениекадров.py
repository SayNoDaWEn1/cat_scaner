import cv2
import os


def extract_frames(video_path, output_folder, frame_skip=10):
    """
    Разбивает видео на кадры.

    :param video_path: Путь к видеофайлу.
    :param output_folder: Папка для сохранения кадров.
    :param frame_skip: Сколько кадров пропускать (например, каждый 10-й кадр).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:  # Сохраняем каждый N-й кадр
            frame_path = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Сохранено {saved_count} кадров в папку {output_folder}")


# Использование
extract_frames("D:\\PythonProject\видео с котом\кот3.mp4", "data/frames", frame_skip=10)