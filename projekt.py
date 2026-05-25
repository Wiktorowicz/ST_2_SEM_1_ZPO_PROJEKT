import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class GreenScreenApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Green Screen")
        self.root.geometry("1800x1000")
        self.root.configure(bg="#202020")

        self.kamera = cv2.VideoCapture(1)

        if not self.kamera.isOpened():
            print("Nie można uruchomić kamery")
            return

        self.tlo = cv2.imread("tlo.jpg")

        if self.tlo is None:
            print("Nie znaleziono obrazu tla!")
            return

        panel = tk.Frame(
            root,
            bg="#303030",
            width=320
        )

        panel.pack(
            side="left",
            fill="y"
        )

        title = tk.Label(
            panel,
            text="Green Screen",
            bg="#303030",
            fg="white",
            font=("Arial", 22, "bold")
        )

        title.pack(pady=20)

        tk.Label(
            panel,
            text="H Min",
            bg="#303030",
            fg="white",
            font=("Arial", 12)
        ).pack()

        self.hMin = tk.Scale(
            panel,
            from_=0,
            to=179,
            orient="horizontal",
            length=250,
            bg="#303030",
            fg="white",
            troughcolor="#505050",
            highlightthickness=0
        )

        self.hMin.set(35)

        self.hMin.pack(pady=10)

        tk.Label(
            panel,
            text="H Max",
            bg="#303030",
            fg="white",
            font=("Arial", 12)
        ).pack()

        self.hMax = tk.Scale(
            panel,
            from_=0,
            to=179,
            orient="horizontal",
            length=250,
            bg="#303030",
            fg="white",
            troughcolor="#505050",
            highlightthickness=0
        )

        self.hMax.set(95)

        self.hMax.pack(pady=10)

        tk.Label(
            panel,
            text="Blur Maski",
            bg="#303030",
            fg="white",
            font=("Arial", 12)
        ).pack()

        self.blurSlider = tk.Scale(
            panel,
            from_=0,
            to=31,
            orient="horizontal",
            length=250,
            bg="#303030",
            fg="white",
            troughcolor="#505050",
            highlightthickness=0
        )

        self.blurSlider.set(15)

        self.blurSlider.pack(pady=10)

        self.colorPreview = tk.Label(
            panel,
            bg="#00ff00",
            width=25,
            height=6
        )

        self.colorPreview.pack(pady=20)

        info = tk.Label(
            panel,
            text="Dostosuj zakres zieleni",
            bg="#303030",
            fg="lightgray",
            font=("Arial", 11)
        )

        info.pack(pady=10)

        self.buttonTlo = tk.Button(
            panel,
            text="Wybierz Tlo",
            font=("Arial", 12, "bold"),
            bg="#505050",
            fg="white",
            command=self.wybierz_tlo
        )

        self.buttonTlo.pack(
            pady=20
        )

        self.tloPreview = tk.Label(
            panel,
            bg="#202020",
            bd=3,
            relief="solid"
        )

        self.tloPreview.pack(
            pady=10
        )

        self.videoFrame = tk.Frame(
            root,
            bg="#202020"
        )

        self.videoFrame.pack(
            expand=True
        )

        self.videoLabel = tk.Label(
            self.videoFrame,
            bg="black"
        )

        self.videoLabel.pack(
            expand=True
        )

        # Start
        self.aktualizuj_podglad_tla()
        self.update_frame()

    def wybierz_tlo(self):

        sciezka = filedialog.askopenfilename(
            filetypes=[
                ("Obrazy", "*.jpg *.png *.jpeg")
            ]
        )

        if sciezka:

            noweTlo = cv2.imread(
                sciezka
            )

            if noweTlo is not None:

                self.tlo = noweTlo

                self.aktualizuj_podglad_tla()

    def aktualizuj_podglad_tla(self):

        miniatura = cv2.resize(
            self.tlo,
            (180, 100)
        )

        miniaturaRGB = cv2.cvtColor(
            miniatura,
            cv2.COLOR_BGR2RGB
        )

        obraz = Image.fromarray(
            miniaturaRGB
        )

        obrazTk = ImageTk.PhotoImage(
            image=obraz
        )

        self.tloPreview.imgtk = obrazTk

        self.tloPreview.configure(
            image=obrazTk
        )

    def update_frame(self):

        sukces, klatka = self.kamera.read()

        if sukces:

            klatka = cv2.flip(
                klatka,
                1
            )

            tloDopasowane = cv2.resize(
                self.tlo,
                (klatka.shape[1], klatka.shape[0])
            )

            hsvObraz = cv2.cvtColor(
                klatka,
                cv2.COLOR_BGR2HSV
            )

            hMin = self.hMin.get()
            hMax = self.hMax.get()

            blurValue = self.blurSlider.get()

            dolnyZielony = np.array([
                hMin,
                60,
                40
            ])

            gornyZielony = np.array([
                hMax,
                255,
                255
            ])

            maska = cv2.inRange(
                hsvObraz,
                dolnyZielony,
                gornyZielony
            )

            kernel = np.ones((5, 5), np.uint8)

            maska = cv2.morphologyEx(
                maska,
                cv2.MORPH_OPEN,
                kernel
            )

            maska = cv2.morphologyEx(
                maska,
                cv2.MORPH_CLOSE,
                kernel
            )

            if blurValue > 0:

                if blurValue % 2 == 0:
                    blurValue += 1

                maska = cv2.GaussianBlur(
                    maska,
                    (blurValue, blurValue),
                    0
                )

            maskaFloat = maska.astype(
                np.float32
            ) / 255.0

            maskaFloat = cv2.merge([
                maskaFloat,
                maskaFloat,
                maskaFloat
            ])

            maskaOdwrotna = 1.0 - maskaFloat

            klatkaFloat = klatka.astype(
                np.float32
            )

            tloFloat = tloDopasowane.astype(
                np.float32
            )

            osoba = klatkaFloat * maskaOdwrotna

            noweTlo = tloFloat * maskaFloat

            wynik = osoba + noweTlo

            wynik = np.clip(
                wynik,
                0,
                255
            ).astype(np.uint8)

            hsvKolor = np.uint8([
                [[(hMin + hMax) // 2, 255, 255]]
            ])

            bgrKolor = cv2.cvtColor(
                hsvKolor,
                cv2.COLOR_HSV2BGR
            )

            b = int(bgrKolor[0][0][0])
            g = int(bgrKolor[0][0][1])
            r = int(bgrKolor[0][0][2])

            hexKolor = '#%02x%02x%02x' % (
                r,
                g,
                b
            )

            self.colorPreview.config(
                bg=hexKolor
            )

            wynikRGB = cv2.cvtColor(
                wynik,
                cv2.COLOR_BGR2RGB
            )

            obraz = Image.fromarray(
                wynikRGB
            )

            obrazTk = ImageTk.PhotoImage(
                image=obraz
            )

            self.videoLabel.imgtk = obrazTk

            self.videoLabel.configure(
                image=obrazTk
            )

        self.root.after(
            10,
            self.update_frame
        )

    def close(self):

        self.kamera.release()
        self.root.destroy()

root = tk.Tk()

app = GreenScreenApp(root)

root.protocol(
    "WM_DELETE_WINDOW",
    app.close
)

root.mainloop()