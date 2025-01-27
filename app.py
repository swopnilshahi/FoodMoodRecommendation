from flask import Flask, request, render_template, redirect, url_for, session, flash
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans
from geopy.distance import geodesic
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'moodfood123'
db = SQLAlchemy(app)

food_data = pd.read_csv('food_choices.csv')

res_data = pd.read_csv('expanded_restaurant_data.csv', encoding='latin-1')


res_data = res_data.loc[(res_data['Country Code'] == 1) & (res_data['City'] == 'Kathmandu')]


res_data = res_data.loc[(res_data['Rating Text'] != 'Not rated') & 
                        (res_data['Longitude'] != 0) & 
                        (res_data['Latitude'] != 0) & 
                        (res_data['Latitude'] < 29)]

res_data['Cuisines'] = res_data['Cuisines'].astype(str)

res_data['No. of Cuisines Offered'] = res_data['Cuisines'].apply(lambda x: len(x.split(',')))


kmeans = KMeans(n_clusters=7, random_state=0).fit(res_data[['Longitude', 'Latitude']])
res_data['pos'] = kmeans.labels_

stop = set(stopwords.words('english'))
stop.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])

lemmatizer = WordNetLemmatizer()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()


    
def search_comfort_food(mood):
    lemmatizer = WordNetLemmatizer()
    stop = set(stopwords.words('english'))
    foodcount = {}
    
    for i in range(len(food_data)):
        temp = [lemmatizer.lemmatize(temps.strip().lower()) for temps in str(food_data["Comfort Food Reason"][i]).split(' ') if temps.strip() not in stop]
        if mood in temp:
            foodtemp = [lemmatizer.lemmatize(temps.strip().lower()) for temps in str(food_data["Comfort Food"][i]).split(',') if temps.strip() not in stop]
            for a in foodtemp:
                if a not in foodcount:
                    foodcount[a] = 1
                else:
                    foodcount[a] += 1
    
    sorted_food = sorted(foodcount, key=foodcount.get, reverse=True)
    return sorted_food[:3] 






def recommend_restaurants(selected_food, user_location, res_data):
    recommended_restaurants = []
    
    
    cuisine_mapping = {
    "pizza": "Pizza",
    "ice cream": "Ice Cream",
    "burger": "Burger",
    "chocolate cake": "Chocolate Cake",
    "pasta": "Pasta",
    "sushi": "Sushi",
    "chocolate": "Chocolate",
    "cookies": "Cookies",
    "macaroni and cheese": "Macaroni and Cheese",
    "fast food": "Fast Food",
    "frozen meals": "Frozen Meals",
    "takeout": "Takeout",
    "fries": "Fries",
    "cake": "Cake",
    "tacos": "Tacos",
    "noodles": "Noodles",
    "steak": "Steak",
    "snack": "Snacks",
    "donuts": "Donuts",
    " nachos": "Nachos",
    "soup": "Soup",
    "hot chocolate": "Hot Chocolate",
    "stews": "Stews",
    "chili": "Chili",
    "grilled cheese": "Grilled Cheese",
    "popcorn": "Popcorn",
    "chips": "Chips",
    "soda": "Soda",
    "stew":"stews",
    "sel roti":"Sel Roti",
    "thukpa":"Thukpa"
}
    
    
    cuisine = cuisine_mapping.get(selected_food.lower(), "")

    if cuisine:
        
        filtered_data = res_data[res_data['Cuisines'].str.contains(cuisine, case=False)]

        if not filtered_data.empty:
            
            sorted_restaurants = filtered_data.sort_values(by='Aggregate Rating', ascending=False)
            
            
            for index, row in sorted_restaurants.iterrows():
                restaurant_location = (row['Latitude'], row['Longitude'])
                distance = geodesic(user_location, restaurant_location).meters
                
                recommended_restaurants.append({
                    'Restaurant Name': row['Restaurant Name'],
                    'Address': row['Address'],
                    'Aggregate Rating': row['Aggregate Rating'],
                    'Distance': distance
                })

               
                if len(recommended_restaurants) >= 3:
                    break

    return recommended_restaurants[:3] 







def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


from sklearn.metrics import silhouette_score

@app.route('/recommend', methods=['GET'])
@login_required
def recommend():
    selected_food = request.args.get('food')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if latitude is None or longitude is None:
        return "Latitude and longitude are required."

    try:
        user_location = (float(latitude), float(longitude))
    except ValueError:
        return "Invalid latitude or longitude provided."

    recommended_restaurants = recommend_restaurants(selected_food, user_location, res_data)
    
    # Extract features used for clustering
    features = res_data[['Longitude', 'Latitude']]

    # Number of clusters
    n_clusters = len(res_data['pos'].unique())

    # Compute Silhouette Score
    silhouette_avg = silhouette_score(features, res_data['pos'])

    return render_template('recommend.html', selected_food=selected_food, 
                           recommended_restaurants=recommended_restaurants, 
                           silhouette_avg=silhouette_avg)




@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            message = "User already registered. Please use another Username and password."
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            message = "Successfully registered. Please login."
    return render_template('register.html', message=message)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/find', methods=['GET'])
def find_food():
    mood = request.args.get('mood')
    comfort_foods = search_comfort_food(mood)
    return render_template('food.html', mood=mood, comfort_foods=comfort_foods)

@app.route('/select_food', methods=['GET'])
def select_food():
    selected_food = request.args.get('food')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    return redirect(url_for('recommend', food=selected_food, latitude=latitude, longitude=longitude))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    else:
        return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)