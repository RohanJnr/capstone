from pathlib import Path
import pandas as pd

clips_dir = Path("/home/ayush/Projects/Capstone/client/output1")


# for _, fil in enumerate(sorted(clips_dir.iterdir())):
#     if fil.is_dir():
#         print(f"Sizes of {fil.stem}")
#         for dir in fil.iterdir():
#             print(f"{dir.stem}: {sum(f.stat().st_size for f in dir.glob('**/*') if f.is_file()) / 1e6} MB")
            

df = pd.read_csv("metrics.csv", header=0)
df["input_size"] = df["input_size"] / 1e6
df["output_size"] = df["output_size"] / 1e6

df.to_csv("metrics.csv", index=False, header=True)