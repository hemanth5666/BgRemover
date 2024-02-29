import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from rembg import remove
from PIL import Image
import concurrent.futures

class DragDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag and Drop Image Processor")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Drag and drop images here", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa;")
        self.layout.addWidget(self.label)

        self.save_button = QPushButton("Save Images", self)
        self.save_button.clicked.connect(self.save_images)
        self.layout.addWidget(self.save_button)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile().endswith('.jpg') or url.toLocalFile().endswith('.png')]
        if file_paths:
            self.process_images(file_paths)

    def process_images(self, file_paths):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for file_path in file_paths:
                futures.append(executor.submit(self.process_image, file_path))
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def process_image(self, file_path):
        try:
            # Load image lazily
            with Image.open(file_path) as input_image:
                # Resize image
                input_image = input_image.resize((800, 600))  # Resize to a smaller resolution
                output_image = remove(input_image, alpha=True, alpha_matting=True)
                output_folder = "output_images"
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                output_path = os.path.join(output_folder, os.path.basename(file_path).split('.')[0] + '.png')
                output_image.save(output_path)
                self.show_image(output_path)
        except Exception as e:
            print("Error processing image:", e)

    def show_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
        else:
            print("Failed to load image")

    def save_images(self):
        output_folder = "output_images"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for filename in os.listdir(output_folder):
            if filename.endswith('.png'):
                os.remove(os.path.join(output_folder, filename))
        self.label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
