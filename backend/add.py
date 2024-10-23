import pandas as pd

# Load the CSV file
df_100 = pd.read_csv("grade_one_questions_100.csv")

# Ensure there is an 'id' column
if 'id' not in df_100.columns:
    df_100['id'] = df_100.index

# Assign weights based on cognitive levels
def assign_weights(label):
    if label == "Remembering":
        return 1
    elif label == "Understanding":
        return 2
    elif label == "Applying":
        return 3

df_100['Weight'] = df_100['Label'].apply(assign_weights)

print(df_100)

# Ensure the rest of your code here...
