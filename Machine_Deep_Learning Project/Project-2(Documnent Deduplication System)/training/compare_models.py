import pandas as pd


class ModelComparator:

    def compare(
        self,
        results
    ):

        df = pd.DataFrame(
            results
        )

        print(df)

        return df