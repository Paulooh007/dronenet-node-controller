def getKeyboardIinputNode():
    lr, fb, ud, yv = 0,0,0,0
    speed = 50
    global informControlCenter
    global objectToFind

    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("a"): yv = speed
    elif kp.getKey("d"): yv = -speed

    if kp.getKey("z"): 
        me.land()
        # me.streamoff()

    if kp.getKey("v"): 
        objectToFind = "CAR"
        sleep(0.2)
    if kp.getKey("b"): 
        objectToFind = "BIKE"
        sleep(0.2)
    if kp.getKey("n"): 
        objectToFind = "PEDESTRIAN"
        sleep(0.2)
    if kp.getKey("c"):
        informControlCenter = not informControlCenter
        if informControlCenter:
            alertCommandCenter(objectToFind)
        sleep(0.2)

    if kp.getKey("t"): 
        me.takeoff()

    return [lr, fb, ud, yv]


def alertCommandCenter(message):
    for i in range(2):  # send message twice; it's UDP!
        s.sendto(bytes(message, "utf-8"), (controlCenterIPAddress, commandCenterPort))
        sleep(1)

def monitorUDP():
    while(1):
        data, address = s.recvfrom(20)
        if len(data) > 1:   # data will now be
            UDPDataAvailable = True # remember to make false whenever you've finished using
            UDPData = data
            print(UDPData)


def findObjects(outputs, img):
    global informControlCenter
    global objectToFind

    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confs = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0] * wT) - w / 2), int((det[1] * hT) - h / 2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)

    for i in indices:
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]

        if classNames[classIds[i]] in classList:

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

            cv2.putText(img, f"{classNames[classIds[i]].upper() if classNames[classIds[i]] != 'person' else 'PEDESTRIAN'} {int(confs[i] * 100)}%",
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
