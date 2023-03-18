import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# variables
folderPath = "Presentation"
width, height = 5000, 7200

# camera setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# list of presentation img
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

# variables
imgNumber = 0
hs, ws = 200, 300
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False

# hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)
buttonDelay = 30  # 10 is number of frames

while True:
    # imports imgs
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 1 denotes horizontal flipping
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrentt = cv2.imread(pathFullImage)
    imgCurrent = cv2.resize(imgCurrentt, (1280, 720))

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)
    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        # print(fingers)
        lmList = hand['lmList']

        indexFinger = lmList[8][0], lmList[8][1]
        # constrain values for easier drawing
        # xVal = int(np.interp(lmList[8][0], [width // 2, w], [0, width]))
        # yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        # indexFinger = xVal, yVal

        if cy <= gestureThreshold:  # if hand is above the gesturethreshold line
            # gesture 1 : left
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

            # gesture 2 : right
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                if imgNumber < len(pathImages) - 1:
                    buttonPressed = True
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

        # gesture 3 : draw pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        # gesture 4 : show pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

    # adding webcam to slide
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape

    imgCurrent[0:hs, w - ws: w] = imgSmall
    cv2.imshow("Slides", imgCurrent)

    # cv2.imshow("Image",img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
