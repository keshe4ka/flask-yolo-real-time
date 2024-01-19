# YOLO DETECTION --------------------
def detection(vid):
    with tf.Session(graph=graph) as sess:

        return_value, frame = vid.read()
        if return_value:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
        else:
            raise ValueError("No image!")

        frame_size = frame.shape[:2]
        image_data = utils.image_preporcess(np.copy(frame), [input_size, input_size])
        image_data = image_data[np.newaxis, ...]
        prev_time = time.time()

        pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
            [return_tensors[1], return_tensors[2], return_tensors[3]],
            feed_dict={return_tensors[0]: image_data})

        pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + num_classes)),
                                    np.reshape(pred_mbbox, (-1, 5 + num_classes)),
                                    np.reshape(pred_lbbox, (-1, 5 + num_classes))], axis=0)

        bboxes = utils.postprocess_boxes(pred_bbox, frame_size, input_size, 0.3)
        bboxes = utils.nms(bboxes, 0.45, method='nms')
        image, detected = utils.draw_bbox(frame, bboxes)

        detected = np.asarray(detected)

        # print("------- frame i ---------")

        class_count = []

        for i in range(len(obj_classes)):  # 80
            obj_count = 0
            for j in range(len(detected)):
                if int(detected[j][5]) == i: obj_count += 1

            class_count = np.append(class_count, obj_count)

        curr_time = time.time()
        exec_time = curr_time - prev_time
        result = np.asarray(image)
        info = "time: %.2f ms" % (1000 * exec_time)
        # cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
        result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return result, class_count