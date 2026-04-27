import cv2
import numpy as np


def Main():
    kamera = cv2.VideoCapture(0)

    if not kamera.isOpened():
        print("Nie można uruchomić kamery")
        return

    while True:
        sukces, klatka = kamera.read()

        if not sukces:
            break

        klatka = cv2.flip(klatka, 1)

        hsvObraz = cv2.cvtColor(klatka, cv2.COLOR_BGR2HSV)

        dolnyZielony = np.array([35, 40, 40])
        gornyZielony = np.array([85, 255, 255])

        maska = cv2.inRange(hsvObraz, dolnyZielony, gornyZielony)

        kernel = np.ones((5, 5), np.uint8)
        maska = cv2.morphologyEx(maska, cv2.MORPH_OPEN, kernel)
        maska = cv2.morphologyEx(maska, cv2.MORPH_DILATE, kernel)

        maskaOdwrotna = cv2.bitwise_not(maska)

        wynik = cv2.bitwise_and(klatka, klatka, mask=maskaOdwrotna)

        cv2.imshow("Oryginal", klatka)
        cv2.imshow("Maska Zielonego", maska)
        cv2.imshow("Bez Tla", wynik)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    Main()