import streamlit as st
import pickle
import pandas as pd
import requests
import gdown

# URL for the file from Google Drive
url = 'https://drive.google.com/uc?id=1973jZbAIkoJUNcwutQ6EEuxIfked4GYS'
output = 'similarity.pkl'

# Download the file from Google Drive
gdown.download(url, output, quiet=False)

# Load the similarity pickle file
with open(output, 'rb') as f:
    similarity = pickle.load(f)

API_KEY = '8265bd1679663a7ea12ac168da84d2e8'

# Function to fetch movie details from TMDB
@st.cache_data
def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US')
    data = response.json()

    # Handle missing poster
    poster_url = "https://via.placeholder.com/500x750?text=No+Image+Available"
    if 'poster_path' in data and data['poster_path']:
        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

    movie_details = {
        'poster': poster_url,
        'title': data.get('title', 'Title not available'),
        'overview': data.get('overview', 'No overview available'),
        'release_date': data.get('release_date', 'Unknown'),
        'rating': data.get('vote_average', 'No rating'),
        'genres': [genre['name'] for genre in data.get('genres', [])],  # Handle missing genres
        'runtime': data.get('runtime', 'Unknown'),
        'homepage': data.get('homepage', None),
        'production_companies': [company['name'] for company in data.get('production_companies', [])],
    }
    return movie_details

# Function to fetch movie recommendations
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found!")
        return []

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        recommended_movies.append(movie_details)
    return recommended_movies

# Load the movies data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# App Title
st.title("🎬 Movie Recommendation System")

# Search for a movie using a dropdown (with search functionality)
selected_movie_name = st.selectbox("Select a movie", movies['title'].values)

# Recommend button
if st.button('Recommend'):
    recommended_movies = recommend(selected_movie_name)

    if recommended_movies:
        # Enhanced UI - Grid layout for movie recommendations
        st.subheader(f"Recommendations based on {selected_movie_name}")

        cols = st.columns(3)  # Create a 3-column grid

        for idx, movie in enumerate(recommended_movies):
            with cols[idx % 3]:  # Distribute movies across columns
                st.image(movie['poster'], use_column_width=True)
                st.markdown(f"**{movie['title']}**")
                st.markdown(f"Rating: {movie['rating']}/10")
                st.markdown(f"Genres: {', '.join(movie['genres'])}")

# Footer or extra info
st.markdown("""
---
💡 **Tip**: Try different movies to get recommendations!
""")