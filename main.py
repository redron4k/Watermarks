import sys
from PyQt5 import QtWidgets
from PyQt5.Qt import *
from activity import *
from steganography import *
from PIL import Image, ImageDraw
from random import randint
from re import findall
from wand.image import Image as Img
import os

VISIBLE = 0
INVISIBLE = 1


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.watermark_name = None
        self.image_name = None
        self.size = None
        self.preview_created = False
        self.mode = VISIBLE

        self.selectImg_btn.clicked.connect(self.select_source_img)
        self.selectWaterMark_btn.clicked.connect(self.select_watermark_img)
        self.save_btn.clicked.connect(self.save)
        self.decrypt_btn.clicked.connect(self.decrypt_invisible)

        self.radioButton.toggled.connect(self.set_watermark_visible)
        self.radioButton_2.toggled.connect(self.set_watermark_invisible)
        self.radioButton_3.toggled.connect(self.set_size_source)
        self.radioButton_4.toggled.connect(self.set_size_custom)
        self.radioButton_5.toggled.connect(self.set_size_max)

        self.size1_edit.editingFinished.connect(self.update_preview)
        self.size2_edit.editingFinished.connect(self.update_preview)
        self.alpha_slider.editingFinished.connect(self.update_preview)
        self.horizontalSlider.sliderReleased.connect(self.update_preview)
        self.verticalSlider.sliderReleased.connect(self.update_preview)

    def select_source_img(self):
        f = self.select_img()
        if f:
            self.image_name = f
            img = Image.open(f)
            self.size = img.size
            self.load_image(f)

    def select_watermark_img(self):
        f = self.select_img()
        if f:
            self.watermark_name = f
            img = Image.open(f)
            img.save("wm.png")

    def select_img(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 
                        'Выберите изображение', 
                        './', 
                        'Image Files (*.png *.jpg *.bmp)')

        return file

    def set_watermark_visible(self):
        self.verticalSlider.setVisible(True)
        self.horizontalSlider.setVisible(True)
        self.alpha_slider.setVisible(True)
        self.radioButton_3.setVisible(True)
        self.radioButton_4.setVisible(True)
        self.radioButton_5.setVisible(True)
        self.size1_edit.setVisible(True)
        self.size2_edit.setVisible(True)
        self.label_2.setVisible(True)
        self.label_4.setVisible(True)
        self.label_5.setVisible(True)
        self.label_6.setVisible(True)
        self.selectWaterMark_btn.setVisible(True)

        self.label_7.setVisible(False)
        self.decrypt_btn.setVisible(False)
        self.invis_mark_edit.setVisible(False)
        self.textBrowser.setVisible(False)

        self.mode = VISIBLE

    def set_watermark_invisible(self):
        self.verticalSlider.setVisible(False)
        self.horizontalSlider.setVisible(False)
        self.alpha_slider.setVisible(False)
        self.radioButton_3.setVisible(False)
        self.radioButton_4.setVisible(False)
        self.radioButton_5.setVisible(False)
        self.size1_edit.setVisible(False)
        self.size2_edit.setVisible(False)
        self.label_2.setVisible(False)
        self.label_4.setVisible(False)
        self.label_5.setVisible(False)
        self.label_6.setVisible(False)
        self.selectWaterMark_btn.setVisible(False)

        self.label_7.setVisible(True)
        self.decrypt_btn.setVisible(True)
        self.invis_mark_edit.setVisible(True)
        self.textBrowser.setVisible(True)

        self.mode = INVISIBLE

    def set_size_source(self):
        self.size1_edit.setDisabled(True)
        self.size2_edit.setDisabled(True)

        self.update_preview()

    def set_size_custom(self):
        self.size1_edit.setDisabled(False)
        self.size2_edit.setDisabled(False)

        self.update_preview()

    def set_size_max(self):
        self.size1_edit.setDisabled(True)
        self.size2_edit.setDisabled(True)

        self.update_preview()

    def update_preview(self):
        if self.radioButton_4.isChecked():
            size1 = self.size1_edit.text()
            size2 = self.size2_edit.text()
            alpha = self.alpha_slider.text()
            if size1 and size2 and alpha:
                name = self.watermark_name
                img = Image.open(name)
                size1 = int(size1) / 100
                size2 = int(size2) / 100
                alpha = int(alpha)
                left, top = self.horizontalSlider.value(), 321 - self.verticalSlider.value()
                x, y = self.size
                left = int((left / 321) * x)
                top = int((top / 321) * x)
                img = img.resize((int(x * size1), int(y * size2)))
                img.save("wm.png")
                tranparent_watermark(self.image_name, "wm.png", alpha, left, top, "preview.jpg")
                self.load_image("preview.jpg")
        elif self.radioButton_3.isChecked():
            alpha = self.alpha_slider.text()
            if alpha:
                name = self.watermark_name
                img = Image.open(name)
                alpha = int(alpha)
                left, top = self.horizontalSlider.value(), 321 - self.verticalSlider.value()
                x, y = self.size
                left = int((left / 321) * x)
                top = int((top / 321) * x)
                img.save("wm.png")
                tranparent_watermark(self.image_name, "wm.png", alpha, left, top, "preview.jpg")
                self.load_image("preview.jpg")
        elif self.radioButton_5.isChecked():
            alpha = self.alpha_slider.text()
            if alpha:
                name = self.watermark_name
                img = Image.open(name)
                alpha = int(alpha)
                img.save("wm.png")
                full_screen_watermark(self.image_name, "wm.png", alpha, "preview.jpg")
                self.load_image("preview.jpg")

        self.preview_created = True

    def load_image(self, filename):
        pixmapImage = QPixmap(filename)
        pixmapImage = pixmapImage.scaled(
            371, 371,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_preview.setPixmap(pixmapImage)

    def decrypt_invisible(self):
        if self.image_name:
            keys_filename = self.image_name.split(".")[0] + "keys.txt"
            text = stega_decrypt(self.image_name, keys_filename)
            self.textBrowser.setText(text)

    def save(self):
        if self.mode:
            text = self.invis_mark_edit.text()
            if text and self.image_name:
                stega_encrypt(self.image_name, text)
        else:
            if self.watermark_name and self.image_name:
                img = Image.open("preview.jpg")
                img.save("result.jpg")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
