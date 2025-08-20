import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import warnings
warnings.filterwarnings('ignore')

# create_phrase_from_hierarchy() and calculate_similarity_sentences() are functions taken from the
# Google Places Enricher utils.py file linked here:
# https://github.com/FerGubert/google_places_enricher/blob/main/src/utils.py
def create_phrase_from_hierarchy(df, columns):
    """
    Creates a phrase by joining hierarchical columns with spaces
    """
    df['phrase'] = df[columns].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    df['phrase'] = df['phrase'].str.replace(' - ', ' ').str.replace('- ', '').str.replace(',', '')
    return df['phrase']

def calculate_similarity_sentences(sentences_estab, sentences_yelp):
    """
    Calculates semantic similarity between Foursquare and Yelp phrases
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode all sentences
    embeddings_estab = model.encode(sentences_estab, convert_to_tensor=True)
    embeddings_yelp = model.encode(sentences_yelp, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_scores = util.cos_sim(embeddings_estab, embeddings_yelp)
    
    # Find best matches
    best_scores = []
    for i in range(len(sentences_estab)):
        best_score = -1
        best_j = -1
        for j in range(len(sentences_yelp)):
            score = cosine_scores[i][j]
            if score > best_score:
                best_score = score
                best_j = j
        best_scores.append({'index': [i, best_j], 'score': best_score})
    
    # Create results dataframe
    phrase_estab = []
    phrase_yelp = []
    score = []
    yelp_parent_1 = []
    yelp_parent_2 = []
    yelp_parent_3 = []
    yelp_leaf = []
    
    for pair in best_scores:
        i, j = pair['index']
        phrase_estab.append(sentences_estab.iloc[i])
        phrase_yelp.append(sentences_yelp.iloc[j])
        score.append(round(float(pair['score']), 4))
        
        # Get Yelp hierarchy details
        yelp_parent_1.append(yelp_df['parent_1'].iloc[j])
        yelp_parent_2.append(yelp_df['parent_2'].iloc[j])
        yelp_parent_3.append(yelp_df['parent_3'].iloc[j])
        yelp_leaf.append(yelp_df['leaf'].iloc[j])
    
    df_score = pd.DataFrame({
        'foursquare_phrase': phrase_estab,
        'yelp_phrase': phrase_yelp,
        'similarity_score': score,
        'yelp_parent_1': yelp_parent_1,
        'yelp_parent_2': yelp_parent_2,
        'yelp_parent_3': yelp_parent_3,
        'yelp_leaf': yelp_leaf
    })
    
    return df_score

# Load the data
foursquare_df = pd.read_csv('foursquare_categories_cleaned2.csv')
yelp_df = pd.read_csv('hierarchical_yelp_categories.csv')

# Fill NaN values with empty strings
foursquare_df = foursquare_df.fillna('')
yelp_df = yelp_df.fillna('')

# Create phrases for both datasets
foursquare_phrases = create_phrase_from_hierarchy(foursquare_df, ['parent_1', 'parent_2', 'parent_3', 'leaf'])
yelp_phrases = create_phrase_from_hierarchy(yelp_df, ['parent_1', 'parent_2', 'parent_3', 'leaf'])

# Calculate similarity and create mapping
mapping_df = calculate_similarity_sentences(foursquare_phrases, yelp_phrases)

# Merge with original Foursquare data to include Category ID and full hierarchy
mapping_df = pd.concat([foursquare_df.reset_index(drop=True), mapping_df], axis=1)

# Filter out low-quality matches (adjust threshold as needed)
threshold = 0.3
filtered_mapping = mapping_df[mapping_df['similarity_score'] >= threshold]

# Save the results
output_path = "foursquare_to_yelp_mapping.csv"
filtered_mapping.to_csv(output_path, index=False)

print(f"Found {len(filtered_mapping)} matches with similarity score >= {threshold}")
print("\nSample of the mapping:")
print(filtered_mapping[['parent_1', 'parent_2', 'parent_3', 'leaf', 'yelp_phrase', 'similarity_score']].head(10))