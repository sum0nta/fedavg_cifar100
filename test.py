import os

img_dir = 'data/cifar100/data/raw/img'
all_images = sorted(os.listdir(img_dir))  # sort to maintain consistency

for i, fname in enumerate(all_images):
    ext = os.path.splitext(fname)[1]
    print(ext)
    os.rename(os.path.join(img_dir, fname), os.path.join(img_dir, f"{i}{ext}"))
import os

img_dir = '../data/cifar100/data/raw/img'  # Adjust if needed
all_images = sorted(os.listdir(img_dir))  # Sort alphabetically

# Optional: filter only .png files
all_images = [f for f in all_images if f.lower().endswith('.png')]

# Temporary rename to avoid name collisions
for i, fname in enumerate(all_images):
    src = os.path.join(img_dir, fname)
    tmp_name = f"temp_{i}.png"
    dst = os.path.join(img_dir, tmp_name)
    os.rename(src, dst)

# Final rename: temp_0.png -> 0.png, temp_1.png -> 1.png, ...
temp_images = sorted(os.listdir(img_dir))
temp_images = [f for f in temp_images if f.startswith("temp_")]

for i, fname in enumerate(temp_images):
    src = os.path.join(img_dir, fname)
    dst = os.path.join(img_dir, f"{i}.png")
    os.rename(src, dst)

print(f"Renamed {len(temp_images)} images to 0.png, 1.png, 2.png, ...")