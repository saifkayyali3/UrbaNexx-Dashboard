import pandas as pd

file_path = 'data/cities.csv'

df = pd.read_csv(file_path)
df_sorted = df.sort_values(by='Country', ascending=True)

df_sorted.to_csv(file_path, index=False, encoding='utf-8-sig')

print(f"{file_path} successfully sorted by alphabetical country order.")
