import os
import time
from onvif import ONVIFCamera
from ultralytics import YOLO
import cv2
import os
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from playsound import playsound


def trigger_alarm(audio_file_path):
    """
    Функция для повышения громкости, воспроизведения звука тревоги
    и возврата громкости на прежний уровень.

    :param audio_file_path: Путь к аудиофайлу (например, 'alert.mp3').
    """
    try:
        audio_file_path = 'alert.mp3'
        # Получение устройства вывода звука
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Сохранение текущей громкости
        original_volume = volume.GetMasterVolumeLevelScalar()

        # Установка громкости на 100%
        volume.SetMasterVolumeLevelScalar(1.0, None)

        # Воспроизведение звука тревоги
        if os.path.exists(audio_file_path):
            playsound(audio_file_path)
        else:
            print(f"Файл {audio_file_path} не найден!")

        # Возврат громкости на прежний уровень
        volume.SetMasterVolumeLevelScalar(original_volume, None)

    except Exception as e:
        print(f"Ошибка при активации тревоги: {e}")


# Замените параметры на свои
ip = "192.168.1.115"
port = 8000
user = "admin"
passwd = "admin"

# Параметры зоны тревоги
alert_zone = (452, 119, 1171, 621)  # x1, y1, x2, y2 (область в центре кадра)
alert_delay = 3  # Задержка перед срабатыванием тревоги (в секундах)
output_folder = "alerts"  # Папка для сохранения скриншотов
os.makedirs(output_folder, exist_ok=True)

# Загрузка обученной модели YOLO
model = YOLO(r'D:\PythonProject\runs\detect\train9\weights\best.pt')

try:
    # Подключение к камере
    camera = ONVIFCamera(ip, port, user, passwd)

    # Получение информации о камере
    device_info = camera.devicemgmt.GetDeviceInformation()
    print(f"Модель: {device_info.Model}, Производитель: {device_info.Manufacturer}")

    # Получение медиа-сервиса
    media_service = camera.create_media_service()

    # Получение профилей (настройки потоков)
    profiles = media_service.GetProfiles()
    profile_token = profiles[0].token  # Используем первый профиль

    # Получение RTSP-ссылки
    stream_uri = media_service.GetStreamUri({
        'StreamSetup': {
            'Stream': 'RTP-Unicast',
            'Transport': 'RTSP'
        },
        'ProfileToken': profile_token
    }).Uri
    stream_uri = "rtsp://admin:admin@192.168.1.115:8554/Streaming/Channels/101"

    print(f"RTSP ссылка: {stream_uri}")

    # Воспроизведение видео с помощью OpenCV
    cap = cv2.VideoCapture(stream_uri)
    if not cap.isOpened():
        print("Не удалось открыть видеопоток")
        exit()

    alert_start_time = None  # Время начала обнаружения объекта в зоне

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Ошибка при получении кадра")
            break

        # Предсказание YOLO на кадре
        results = model(frame)

        # Отрисовка центральной зоны
        x1, y1, x2, y2 = alert_zone
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Проверка наличия объекта в зоне
        proximity_threshold = 10  # Задаем расстояние для близости к зоне

        for result in results[0].boxes.xyxy:
            obj_x1, obj_y1, obj_x2, obj_y2 = result
            print(f"Объект: x1={obj_x1}, y1={obj_y1}, x2={obj_x2}, y2={obj_y2}")

            # Проверка на пересечение или близость к зоне
            if (
                    obj_x2 >= x1 - proximity_threshold and  # Объект касается или ближе к левой границе
                    obj_x1 <= x2 + proximity_threshold and  # Объект касается или ближе к правой границе
                    obj_y2 >= y1 - proximity_threshold and  # Объект касается или ближе к верхней границе
                    obj_y1 <= y2 + proximity_threshold  # Объект касается или ближе к нижней границе
            ):
                if alert_start_time is None:
                    alert_start_time = time.time()
                    print("Начало отсчёта времени тревоги")
                elif time.time() - alert_start_time >= alert_delay:
                    # Срабатывание тревоги
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    output_path = os.path.join(output_folder, f"alert_{timestamp}.jpg")
                    cv2.imwrite(output_path, frame)
                    print(f"Тревога! Сохранен скриншот: {output_path}")
                    trigger_alarm("alert.mp3")  # Звук тревоги
                    alert_start_time = None  # Сброс времени тревоги
                break
        else:
            # Если объект покинул зону или нет близости, сброс таймера
            alert_start_time = None

        # Отображение результатов
        annotated_frame = results[0].plot()  # Рисуем предсказания на кадре
        cv2.imshow("Видео с камеры (с YOLO)", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Нажмите 'q', чтобы выйти
            break

    cap.release()
    cv2.destroyAllWindows()

except Exception as e:
    print(f"Ошибка подключения: {e}")

