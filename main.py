import streamlit as st
import pandas as pd
import pickle
import requests
import base64

from zipfile import ZipFile
with ZipFile("similarity.zip", 'r') as zObject:
  
    # Extracting specific file in the zip
    # into a specific location.
    zObject.extract("similarity.pkl", path=(""))
zObject.close()

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('image.jpg')
def fetch_poster(movie_id, retries=0):
    try:
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=b1041507cc5370a36fa6ac21b683b753&language=en-US'.format(movie_id))
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return None
    except requests.exceptions.RequestException:
        # Completely suppress messages on the web app
        pass  # Do nothing, don't display any message

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index
    if len(movie_index) == 0:
        st.warning("Movie not found in the dataset.")
        return [], []  # Return empty lists if movie not found
    movie_index = movie_index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
            recommended_movies.append(movies.iloc[i[0]].title)

    # If fewer than 5 recommendations are available, display a warning
    if len(recommended_movies) < 10:
        st.warning("Only {} recommendations available.".format(len(recommended_movies)))

    return recommended_movies, recommended_movies_posters


movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movies = pd.DataFrame(movie_dict)

st.title("Movie Recommendation system")

selected_movie_name = st.selectbox('Select a movie', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(10)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                # Use a placeholder image or informative message
                st.info("Poster not available.")  # Informative message

