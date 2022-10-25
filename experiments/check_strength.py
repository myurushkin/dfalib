import pandas as pd
import json, tqdm
from dafna import strength

if __name__ == "__main__":
    input_file = "random"
    for input_file in "random", "tandem":
        with open(input_file + ".json") as f:
            data = json.load(f)
        strings = list(data.keys())

        result = pd.DataFrame(columns=['String', "GQD", "IMT", "TRP", "HRP"])

        for str in tqdm.tqdm(strings):
            result = result.append(
                {
                    "String": str,
                    "GQD": strength.gqd_max_strength(str),
                    "IMT": max(strength.i_motif_max_strength(str, False), strength.i_motif_max_strength(str, True)),
                    "TRP": strength.triplex_max_strength(str),
                    "HRP": strength.hairpin_max_strength(str)
                },
                ignore_index=True)

        result.to_csv(input_file + "_output.csv", index=False)