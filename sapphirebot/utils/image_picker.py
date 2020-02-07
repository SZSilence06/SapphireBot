# coding=utf-8
from nonebot import get_bot
import os
import random

class ImagePicker(object):
    def __init__(self, image_dir: str):
        self.cq_dir = get_bot().config.CQ_DIR
        self.img_dir = os.path.join(self.cq_dir, 'data', 'image')
        self.image_dir = os.path.join(self.img_dir, image_dir)
        self.images = []

        self.load_images()

    def load_images(self):
        for root, dirs, filenames in os.walk(self.image_dir):
            for f in filenames:
                full_path = os.path.join(root, f)
                self.images.append(os.path.relpath(full_path, self.img_dir))

    def pick_one_image(self):
        return random.choice(self.images)