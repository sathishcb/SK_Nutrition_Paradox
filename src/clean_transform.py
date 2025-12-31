import pandas as pd
import pycountry

SPECIAL_CASES = {
    "GLOBAL": "Global",
    "WB_LMI": "Low & Middle Income",
    "WB_HI": "High Income",
    "WB_LI": "Low Income",
    "EMR": "Eastern Mediterranean Region",
    "EUR": "Europe",
    "AFR": "Africa",
    "SEAR": "South-East Asia Region",
    "WPR": "Western Pacific Region",
    "AMR": "Americas Region",
    "WB_UMI": "Upper Middle Income"
}

GENDER_MAP = {
    "SEX_MLE": "Male",
    "SEX_FMLE": "Female",
    "SEX_BTSX": "Both"
}

def convert_country(code):
    if code in SPECIAL_CASES:
        return SPECIAL_CASES[code]
    try:
        return pycountry.countries.get(alpha_3=code).name
    except:
        return code

def clean_one(df, is_obesity=False, is_malnutrition=False):
    # Add default age_group if missing
    if "age_group" not in df.columns:
        df["age_group"] = "Adult" if is_obesity else "Child/Adolescent"

    # Keep only required columns
    df = df[["ParentLocation", "Dim1", "TimeDim", "Low", "High", "NumericValue", "SpatialDim", "age_group"]]

    # Rename columns
    df = df.rename(columns={
        "TimeDim": "Year",
        "Dim1": "Gender",
        "NumericValue": "Mean_Estimate",
        "Low": "LowerBound",
        "High": "UpperBound",
        "ParentLocation": "Region",
        "SpatialDim": "Country"
    })

    # Standardize Gender
    df["Gender"] = df["Gender"].apply(lambda x: GENDER_MAP.get(x, "Both"))

    # Convert country code → full country name
    df["Country"] = df["Country"].apply(convert_country)

    # Filter 2012–2022
    df = df[(df["Year"] >= 2012) & (df["Year"] <= 2022)]

    # Add CI Width
    df["CI_Width"] = df["UpperBound"] - df["LowerBound"]

    # Add Levels
    if is_obesity:
        df["Obesity_Level"] = df["Mean_Estimate"].apply(
            lambda x: "High" if x >= 30 else ("Moderate" if x >= 25 else "Low")
        )
    if is_malnutrition:
        df["Malnutrition_Level"] = df["Mean_Estimate"].apply(
            lambda x: "High" if x >= 20 else ("Moderate" if x >= 10 else "Low")
        )

    return df

def clean_all(data):
    obesity = pd.concat([data["obesity_adults"], data["obesity_children"]])
    malnutrition = pd.concat([data["malnutrition_adults"], data["malnutrition_children"]])

    return {
        "obesity": clean_one(obesity, is_obesity=True),
        "malnutrition": clean_one(malnutrition, is_malnutrition=True)
    }
