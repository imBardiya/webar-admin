import os
import shutil

OUTPUT = "static/all.mind"
INPUT_FOLDER = "static/uploads"

with open(OUTPUT, "wb") as outfile:
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".mind"):
            with open(os.path.join(INPUT_FOLDER, filename), "rb") as f:
                shutil.copyfileobj(f, outfile)
