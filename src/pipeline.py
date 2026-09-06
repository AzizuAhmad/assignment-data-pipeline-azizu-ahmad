import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "automobileEDA_dirty_training.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "automobileEDA_processed.csv")


def load_data():
    # path = input("Masukkan path dataset CSV: ")
    data = pd.read_csv(RAW_PATH)
    return data

def show_data(data):
    print("=" * 60)
    print("PEMERIKSAAN KONDISI AWAL DATASET")
    print("=" * 60)

    print("\n=== 5 baris pertama ===")
    print(data.head(5))

    print("\n=== Jumlah baris dan kolom ===")
    print(data.shape)

    print("\n=== Informasi setiap kolom dan tipe datanya ===")
    data.info()

    print("\n=== Jumlah missing values setiap kolom ===")
    print(data.isnull().sum())

    print("\n=== Data duplikat ===")
    print(data[data.duplicated(keep= False)])

    print("\n=== Nilai unik pada kolom kategorikal ===")
    cat_col = data.select_dtypes(include=["str", "category"]).columns
    for col in cat_col:
        print(f"\nKolom          : {col}")
        print(f"Kategori unik  : {data[col].nunique()}")
        print(f"Daftar nilai   : {data[col].unique()}")

# Cleaning data
def cleaning_data(data):

    df = data.copy()

    def is_likely_categorical(series, threshold=10):
            return series.nunique(dropna=True) <= threshold

    # cleaning placeholder
    df = df.replace(['N/A',"-","unknown"], np.nan)
    print("=== Info dataset setelah placeholder (N/A, -, unknown) diganti NaN ===")
    df.info()

    # Checking dytype
    int_cols = df.select_dtypes(include = ["int64","int32","float64"]).columns
    true_numeric_cols = []
    pseudo_cat_cols = []
    
    for col in int_cols:
        if is_likely_categorical(df[col]):
            pseudo_cat_cols.append(col)
        else:
            true_numeric_cols.append(col)

    print(f"\n=== Kolom numerik asli ===\n{true_numeric_cols}")
    print(f"\n=== Kolom numerik yang sebenarnya kategorikal ===\n{pseudo_cat_cols}")

    cat_cols = df.select_dtypes(include = ["str","category"]).columns
    print(f"\n=== Kolom kategorikal ===\n{cat_cols}")

    df['transaction_date'] = pd.to_datetime(df["transaction_date"], format="mixed",errors="coerce")
    date_cols = df.select_dtypes(include = ["datetime64"]).columns
    print(f"\n=== Kolom tanggal ===\n{date_cols}")

    # missing value
    print(f"\n=== Missing value (sebelum diisi) ===\n{df.isnull().sum()[df.isnull().sum()>0]}")
    # numeric   
    int_cols_miss = [col for col in true_numeric_cols if df[col].isnull().sum() > 0]
    for col in int_cols_miss:
        df[col] = df[col].fillna(df[col].mean())

    # categorical with mode handle
    cat_cols_miss = [col for col in cat_cols if df[col].isnull().sum() > 0]
    for col in cat_cols_miss:
        df[col] = df[col].fillna(df[col].mode()[0])

    print(f"\n=== Missing value (sesudah diisi) ===\n{df.isnull().sum()[df.isnull().sum()>0]}")

    #duplikat
    dup = df[df.duplicated(keep="first")]
    print("\n=== Baris duplikat ===")
    print(f"Jumlah baris duplikat: {len(dup)}")
    print(dup)

    df.drop_duplicates(inplace= True, keep = "first")
    dup = df[df.duplicated(keep="first")]
    print("\n=== Setelah baris duplikat dihapus ===")
    print(f"Jumlah baris duplikat tersisa: {len(dup)}")

    # standarisasi categorical values
    for col in cat_cols:
        if df[col].dtype in ['category','str']:
            df[col] = df[col].str.strip().str.lower().str.replace(r'\s','',regex = True)
    print(f"\n=== Data setelah standarisasi nilai kategorikal ===\n{df.head()}")

    # ringkasan perubahan cleaning
    changed_cols = [
        col for col in df.columns
        if not df[col].reset_index(drop=True).equals(data[col].loc[df.index].reset_index(drop=True))
    ]
    print("\n=== Ringkasan cleaning ===")
    print(f"Jumlah baris sebelum  : {len(data)}")
    print(f"Jumlah baris sesudah  : {len(df)}")
    print(f"Baris duplikat dihapus : {len(data) - len(df)}")
    print(f"Jumlah kolom           : {df.shape[1]}")
    print(f"Kolom yang berubah     : {changed_cols}")

    # outlier (kondisi data saat  ini terlelu sedikit)
    # print(df[int_cols].describe())
    # def detect_outliers_iqr(series):
    #     Q1 = series.quantile(0.25)
    #     Q3 = series.quantile(0.75)
    #     IQR = Q3 - Q1
    #     lower = Q1 - 1.5 * IQR
    #     upper = Q3 + 1.5 * IQR
    #     return series[(series < lower) | (series > upper)]

    # def remove_outliers_iqr(df, cols):
    #     df_clean = df.copy()
    #     for col in cols:
    #         Q1 = df_clean[col].quantile(0.25)
    #         Q3 = df_clean[col].quantile(0.75)
    #         IQR = Q3 - Q1
    #         lower = Q1 - 1.5 * IQR
    #         upper = Q3 + 1.5 * IQR
    #         df_clean = df_clean[(df_clean[col] >= lower) & (df_clean[col] <= upper)]
    #     return df_clean

    # for col in int_cols:
    #     outlier = detect_outliers_iqr(df[col])
    #     if len(outlier) > 0:
    #         print(f"{col}: {len(outlier)} outliers") 

    # df = remove_outliers_iqr(df,int_cols)
    # print(df.info())

    return df


def transform(data):
    dfClean = data.copy()

    cat_cols = dfClean.select_dtypes(include = ["str","category"]).columns
    print("=" * 60)
    print("TRANSFORMASI: ENCODING DATA KATEGORIKAL")
    print("=" * 60)
    print("\n=== Distribusi nilai tiap kolom kategorikal (sebelum encoding) ===")
    for col in cat_cols:
        print(f"\n{col}:\n{dfClean[col].value_counts()}")

    le = LabelEncoder()
    binary_cols = ['aspiration', 'num-of-doors', 'engine-location']
    for col in binary_cols:
        dfClean[col] = le.fit_transform(dfClean[col])

    # ordinal
    horsepower_order = {'low': 0, 'medium': 1, 'high': 2}
    dfClean['horsepower-binned'] = dfClean['horsepower-binned'].map(horsepower_order)

    cyl_order = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'eight': 8, 'twelve': 12}
    dfClean['num-of-cylinders'] = dfClean['num-of-cylinders'].map(cyl_order)

    ohe_cols = ['body-style', 'drive-wheels', 'engine-type', 'fuel-system']
    dfClean = pd.get_dummies(dfClean, columns=ohe_cols, drop_first=True)

    freq_map = dfClean['make'].value_counts(normalize=True)
    dfClean['make_encoded'] = dfClean['make'].map(freq_map)
    dfClean = dfClean.drop(columns=['make'])

    candidate_num_cols = [
        'normalized-losses', 'wheel-base', 'length', 'width', 'height',
        'curb-weight', 'engine-size', 'bore', 'stroke', 'compression-ratio',
        'horsepower', 'peak-rpm', 'city-mpg', 'highway-mpg', 'price', 'city-L/100km'
    ]
    scale_cols = [c for c in candidate_num_cols
                  if c in dfClean.columns and pd.api.types.is_numeric_dtype(dfClean[c])]

    before_scaling = dfClean[scale_cols].head().copy()

    scaler = MinMaxScaler()
    dfClean[scale_cols] = scaler.fit_transform(dfClean[scale_cols])

    after_scaling = dfClean[scale_cols].head().copy()
    print("\n" + "=" * 60)
    print("TRANSFORMASI: NORMALISASI MIN-MAX SCALING")
    print("=" * 60)
    print(f"\nKolom yang dinormalisasi:\n{scale_cols}")
    print(f"\n--- Nilai SEBELUM scaling (5 baris pertama) ---\n{before_scaling}")
    print(f"\n--- Nilai SESUDAH scaling (5 baris pertama) ---\n{after_scaling}")
    print(f"\n--- Rentang nilai tiap kolom setelah scaling ---\n{dfClean[scale_cols].agg(['min', 'max']).T}")

    print("\n=== Info dataset akhir setelah transformasi ===")
    dfClean.info()

    return dfClean


def save_data(data, path=PROCESSED_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data.to_csv(path, index=False)
    print("\n" + "=" * 60)
    print("LOAD: SIMPAN PROCESSED DATASET")
    print("=" * 60)
    print(f"Lokasi : {path}")
    print(f"Ukuran : {data.shape[0]} baris x {data.shape[1]} kolom")
    return path


def main():
    data = load_data()
    show_data(data)
    df_clean = cleaning_data(data)
    df_processed = transform(df_clean)
    save_data(df_processed)


if __name__ == "__main__":
    main()


