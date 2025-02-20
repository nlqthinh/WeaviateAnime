import pandas as pd

def clean_anime_data(file_path):
    # Load the dataset
    anime_data = pd.read_csv(file_path)

    # Drop duplicates
    anime_data.drop_duplicates(subset=['mal_id'], inplace=True)

    # Handle missing values
    anime_data['type'].fillna('Unknown', inplace=True)
    anime_data['score'].fillna(anime_data['score'].median(), inplace=True)
    anime_data['scored_by'].fillna(0, inplace=True)
    anime_data['episodes'].fillna(0, inplace=True)
    anime_data['aired_from'] = pd.to_datetime(anime_data['aired_from'], errors='coerce')
    anime_data['aired_to'] = pd.to_datetime(anime_data['aired_to'], errors='coerce')
    anime_data['source'].fillna('Unknown', inplace=True)
    anime_data['rating'].fillna('Unknown', inplace=True)

    # Extract year and month from aired_from
    anime_data['aired_year'] = anime_data['aired_from'].dt.year
    anime_data['aired_month'] = anime_data['aired_from'].dt.month

    # Replace NaN values in aired_year and aired_month with 0 and ensure they are floats
    anime_data['aired_year'].fillna(0, inplace=True)
    anime_data['aired_month'].fillna(0, inplace=True)
    anime_data['aired_year'] = anime_data['aired_year'].astype(float)
    anime_data['aired_month'] = anime_data['aired_month'].astype(float)

    # Normalize categorical columns (e.g., convert string lists to actual lists)
    list_columns = ['genres', 'themes', 'demographics', 'studios', 'producers', 'licensors']
    for col in list_columns:
        anime_data[col] = anime_data[col].apply(lambda x: eval(x) if pd.notnull(x) else [])

    # Replace NaN values in premiered_year with 0 and ensure it is a float
    anime_data['premiered_year'].fillna(0, inplace=True)
    anime_data['premiered_year'] = anime_data['premiered_year'].astype(float)

    # Create a column for total members (scored_by + members)
    anime_data['total_members'] = anime_data['scored_by'] + anime_data['members']

    # Drop columns with excessive missing values, except for 'main_picture'
    anime_data.drop(columns=['background', 'trailer_url'], inplace=True)

    # Save the cleaned dataset
    cleaned_file_path = file_path.replace('.csv', '_cleaned.csv')
    anime_data.to_csv(cleaned_file_path, index=False)

    return cleaned_file_path

# Run the cleaning function
cleaned_file_path = clean_anime_data('anime.csv')
cleaned_file_path
