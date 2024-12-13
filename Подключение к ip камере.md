stream_uri  = "rtsp://admin:admin@192.168.1.115:8554/Streaming/Channels/101"
# Код
```
from onvif import ONVIFCamera  
import cv2  
  
# Замените параметры на свои  
ip = "192.168.1.115"  
port = 8000  
user = "admin"  
passwd = "admin"  
  
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
  
    # Получение RTSP-ссылки    stream_uri = media_service.GetStreamUri({  
        'StreamSetup': {  
            'Stream': 'RTP-Unicast',  
            'Transport': 'RTSP'  
        },  
        'ProfileToken': profile_token  
    }).Uri  
    stream_uri  = "rtsp://admin:admin@192.168.1.115:8554/Streaming/Channels/101"  
  
    print(f"RTSP ссылка: {stream_uri}")  
  
    # Воспроизведение видео с помощью OpenCV  
    cap = cv2.VideoCapture(stream_uri)  
    if not cap.isOpened():  
        print("Не удалось открыть видеопоток")  
        exit()  
  
    while True:  
        ret, frame = cap.read()  
        if not ret:  
            print("Ошибка при получении кадра")  
            break  
  
        cv2.imshow("Видео с камеры", frame)  
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Нажмите 'q', чтобы выйти  
            break  
  
    cap.release()  
    cv2.destroyAllWindows()  
  
except Exception as e:  
    print(f"Ошибка подключения: {e}")
```