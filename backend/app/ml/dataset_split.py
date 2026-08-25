import os
import pandas as pd

from sklearn.model_selection import train_test_split


class DatasetSplitter:
    """
    Split the prepared dataset into
    training, validation, and testing sets.
    """

    def __init__(self):

        current_dir = os.path.dirname(__file__)

        self.dataset_path = os.path.join(
            current_dir,
            "training_data.csv"
        )

    def split_dataset(self):

        # -----------------------------
        # Load dataset
        # -----------------------------
        df = pd.read_csv(self.dataset_path)

        # Convert labels to integers
        df["Label"] = (
            df["Label"]
            .astype(str)
            .str.strip()
            .map({
                "Yes": 1,
                "No": 0
            })
        )

        # Features and target
        X = df.drop(columns=["Label"])
        y = df["Label"]

        # -----------------------------
        # 70% Train
        # 30% Temp
        # -----------------------------
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=42,
            stratify=y
        )

        # -----------------------------
        # 15% Validation
        # 15% Test
        # -----------------------------
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=42,
            stratify=y_temp
        )

        print("\n========== DATASET SPLIT ==========\n")

        print(f"Total Samples      : {len(df)}")
        print(f"Training Samples   : {len(X_train)}")
        print(f"Validation Samples : {len(X_val)}")
        print(f"Testing Samples    : {len(X_test)}")

        print("\nSplit Ratio")
        print(
            f"{len(X_train)/len(df):.0%} Training | "
            f"{len(X_val)/len(df):.0%} Validation | "
            f"{len(X_test)/len(df):.0%} Testing"
        )

        return (
            X_train,
            X_val,
            X_test,
            y_train,
            y_val,
            y_test
        )


if __name__ == "__main__":

    splitter = DatasetSplitter()

    splitter.split_dataset()