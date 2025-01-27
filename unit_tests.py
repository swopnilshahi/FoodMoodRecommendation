import unittest
from app import search_comfort_food, recommend_restaurants

# Define sample data for testing recommend_restaurants function
res_data = [
    {
        'Restaurant Name': 'Sherpa Supper',
        'Rating': 4.8,
        'Address': '37, 37 Street, Nearby Temple',
        'Latitude': 27.7172,
        'Longitude': 85.324
    },
    {
        'Restaurant Name': 'Himalayan Delight',
        'Rating': 4.7,
        'Address': '190, Chabahil Chowk, Manaslu Mountain Range',
        'Latitude': 27.7215,
        'Longitude': 85.3206
    },
    {
        'Restaurant Name': 'Pizza King',
        'Rating': 3.5,
        'Address': '144, Gairidhara Road, Jomsom Bazaar',
        'Latitude': 27.7248,
        'Longitude': 85.3135
    }
]

class TestApp(unittest.TestCase):

    def test_select_comfort_food_valid_mood(self):
        valid_mood = "happy"
        result = search_comfort_food(valid_mood)
        expected_foods = ['pizza', 'ice cream', 'burger']
        self.assertEqual(result, expected_foods)

    def test_select_comfort_food_invalid_mood(self):
        invalid_mood = "sad"
        result = search_comfort_food(invalid_mood)
        self.assertFalse(result)

    def test_login_required_redirect(self):
        with self.assertRaises(Exception):
            login_required_function()

def recommend_restaurants(selected_food, user_location, res_data):
    recommended_restaurants = []
    
    cuisine_mapping = {
        "pizza": "Pizza",
        "ice cream": "Ice Cream",
        "burger": "Burger",
        # Add more mappings as needed
    }
    
    cuisine = cuisine_mapping.get(selected_food.lower(), "")

    if cuisine:
        filtered_restaurants = [
            restaurant for restaurant in res_data
            if cuisine in restaurant.get('Cuisines', '').lower()
        ]

        if filtered_restaurants:
            sorted_restaurants = sorted(filtered_restaurants, key=lambda x: x.get('Aggregate Rating', 0), reverse=True)
            
            for restaurant in sorted_restaurants:
                restaurant_location = (restaurant.get('Latitude', 0), restaurant.get('Longitude', 0))
                distance = geodesic(user_location, restaurant_location).meters
                
                recommended_restaurants.append({
                    'Restaurant Name': restaurant.get('Restaurant Name', ''),
                    'Address': restaurant.get('Address', ''),
                    'Aggregate Rating': restaurant.get('Aggregate Rating', 0),
                    'Distance': distance
                })

                if len(recommended_restaurants) >= 3:
                    break

    return recommended_restaurants[:3]


if __name__ == '__main__':
    unittest.main()
