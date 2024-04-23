import math
import random

import cv2
import numpy as np
from ultralytics import YOLO

from app import settings


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(settings.camera)
        self.model = YOLO(settings.path_model)
        self.item_person_vector = dict()

    def get_count(self):
        person_count = 0
        items_count = len(self.item_person_vector)
        left_items_count = sum(1 for v in self.item_person_vector.values() if v is None)
        return person_count, items_count, left_items_count

    def gen_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                person_count = 0
                laptop_count = 0
                results = self.model(frame, stream=True)
                for r in results:
                    boxes = r.boxes

                    for box in boxes:
                        # bounding box
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

                        # put box in cam
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                        # confidence
                        confidence = math.ceil((box.conf[0] * 100)) / 100
                        # print("Confidence --->", confidence)

                        # class name
                        cls = int(box.cls[0])
                        if cls == 0:
                            person_count += 1
                        elif cls == 1:
                            laptop_count += 1
                        # print("Class name -->", settings.class_names[cls])

                        # object details
                        org = [x1, y1]
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        fontScale = 1
                        color = (255, 0, 0)
                        thickness = 2

                        print(f'PERSONS: {person_count}, LAPTOPS: {laptop_count}')

                        cv2.putText(frame, settings.class_names[cls], org, font, fontScale, color, thickness)

                ret, buffer = cv2.imencode('.jpg', frame)

                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def gen_frames_2(self):

        colors = [(random.randint(0, 255), random.randint(0, 255),
                   random.randint(0, 255)) for j in range(20)]

        # Высота и ширина видео файла
        cap_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT).__int__()
        cap_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH).__int__()

        # Разрешение изображения должно быть кратно сетевому шагу 32 для YOLOv8. Иначе warning и авто корректировка
        cap_height = round(cap_height / 32) * 32
        cap_width = round(cap_width / 32) * 32

        # пропорции разрешения экрана
        frame_proportions = cap_width / cap_height / 100

        # дистанция для определения владельца предмета
        distance_threshold = 5.7

        # {item_id: person_id}
        item_person_association = dict()

        # {item_id: vector}
        # self.item_person_vector = dict()

        while self.camera.isOpened():
            # Читаем кадр из видео
            success, frame = self.camera.read()

            if success:
                # результаты
                results = self.model.track(
                    frame, persist=True,  # Сохранение идентификаторов ранее обнаруженных объектов
                    imgsz=(cap_height, cap_width),  # Размер изображения для вывода
                    # tracker='botsort_custom.yaml'
                )

                # Получение объекта Boxes
                boxes = results[0].boxes

                # Если на кадре есть объекты
                if boxes.id is not None:

                    class_dict = results[0].names  # словарь классов в model
                    objs_box = boxes.xywh.cpu()  # боксы объектов в кадре
                    list_objs_id = boxes.id.int().cpu().tolist()  # id объектов в кадре
                    objs_cls = boxes.cls.int().cpu().tolist()  # классы объектов в кадре
                    objs_scores = boxes.conf.tolist()  # score объектов в кадре

                    # Получаем списки индексов предметов и людей на текущем кадре
                    items_class = ['Handbag', 'Luggage-and-bags', 'Wheelchair',
                                   'backpack', 'handbag', 'suitcase', 'bird']  # stock yolo class

                    person_class = ['Human-body', 'person']  # stock yolo class

                    item_index_list = [index for index, value in enumerate(objs_cls) if
                                       class_dict[value] in items_class]
                    person_index_list = [index for index, value in enumerate(objs_cls) if
                                         class_dict[value] in person_class]

                    '''
                    Сопоставление предмет-человек для всех предметов в кадре
                    '''
                    for item_index in item_index_list:
                        item_id = list_objs_id[item_index]

                        # если для предмета не определен владелец
                        if item_id not in item_person_association:
                            # центр бокса предмета [item_x, item_y]
                            item_center_point = [float(i) for i in objs_box[item_index][:2]]

                            # определяем владельца
                            for person_index in person_index_list:

                                # центр бокса человека [person_x, person_y]
                                person_center_point = [float(i) for i in objs_box[person_index][:2]]
                                vector_between_centers_boxes = np.array([item_center_point,
                                                                         person_center_point],
                                                                        np.int32).reshape((-1, 1, 2))

                                person_center_point_with_coef = [person_center_point[0] ** 2 / cap_width,
                                                                 person_center_point[1] ** 2 / cap_height]
                                '''Евклидово расстояние-это норма L2 вектора
                                функция np.linalg.norm() по умолчанию использует ord=None (for vectors 2-norm)'''
                                distance_between_boxes = np.linalg.norm(np.array([item_center_point,
                                                                                  person_center_point_with_coef],
                                                                                 np.int32).reshape((-1, 1, 2)))

                                # если расстояние между боксами удовлетворяет условию определяем человека как владельца предмета
                                if distance_between_boxes < distance_threshold:
                                    item_person_association[item_id] = list_objs_id[
                                        person_index]  # {item_id: person_id}
                                    self.item_person_vector[item_id] = vector_between_centers_boxes  # {item_id: vector}
                                # если расстояние не удовлетворяет условию и нет владельца - владелец и вектор None
                                else:
                                    if item_id not in item_person_association:
                                        item_person_association[item_id] = None  # {item_id: person_id}
                                        self.item_person_vector[item_id] = None  # {item_id: vector}

                        # если для предмета определен владелец
                        else:
                            person_id = item_person_association[item_id]

                            # если владелец в кадре - обновляем значение вектора
                            if person_id in list_objs_id:
                                person_index = list_objs_id.index(person_id)
                                # центр бокса предмета [item_x, item_y]
                                item_center_point = [float(i) for i in objs_box[item_index][:2]]
                                # центр бокса человека [person_x, person_y]
                                person_center_point = [float(i) for i in objs_box[person_index][:2]]
                                vector_between_centers_boxes = np.array([item_center_point,
                                                                         person_center_point],
                                                                        np.int32).reshape((-1, 1, 2))
                                self.item_person_vector[item_id] = vector_between_centers_boxes  # {item_id: vector}

                            # если владелец не в кадре - вектор None
                            else:
                                # {item_id: vector}
                                self.item_person_vector[item_id] = None

                    '''если предмет не в кадре - вектор None'''
                    for item_id in item_person_association:
                        if item_id not in list_objs_id:
                            # {item_id: vector}
                            self.item_person_vector[item_id] = None

                    '''Визуализация на кадр'''
                    # Отображение связи предмет-человек
                    cv2.polylines(frame,
                                  [vector for vector in self.item_person_vector.values()],
                                  isClosed=True, color=(0, 0, 255),  # BGR red
                                  thickness=5)

                    # надпись "оставлено" для объектов
                    for item_id in item_person_association.keys():

                        # если объект в кадре
                        if item_id in list_objs_id:
                            item_index = list_objs_id.index(item_id)
                            try:
                                # item_person_vector =  {item_id: vector}
                                item_vector = self.item_person_vector[item_id]
                                # если вектор None
                                if item_vector is None:
                                    x, y, w, h = [int(i) for i in objs_box[item_index]]
                                    text_item = 'leave'
                                    cv2.rectangle(frame,
                                                  (x - w // 2, y - 13),
                                                  (x + w // 2 + len(text_item) + 1, y + 2),
                                                  (0, 0, 0),  # черный цвет
                                                  -1)

                                    cv2.putText(frame, text_item, (x - w // 2 + 5, y),
                                                cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

                            except (KeyError, ValueError):
                                continue

                    #  Для каждого объекта в кадре
                    for obj_id in list_objs_id:
                        # Данные объекта
                        obj_index = list_objs_id.index(obj_id)
                        x, y, w, h = [int(i) for i in objs_box[obj_index]]

                        # Отображение бокса объекта
                        cv2.rectangle(frame,
                                      (x - w // 2, y - h // 2),  # верхний левый угол
                                      (x + w // 2, y + h // 2),  # нижний правый угол
                                      (colors[obj_index % len(colors)]),  # уникальный цвет по индексу
                                      3)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # Прервать цикл если видео закончилось
                break
