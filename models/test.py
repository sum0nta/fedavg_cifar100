import os

img_dir = '/data/cifar100/data/raw/img'
all_images = sorted(os.listdir(img_dir))  # sort to maintain consistency

for i, fname in enumerate(all_images):
    ext = os.path.splitext(fname)[1]
    os.rename(os.path.join(img_dir, fname), os.path.join(img_dir, f"{i}{ext}"))
