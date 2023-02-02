from flask import Flask, request, redirect, session
from pyhtml import html, body, p, h1, form, label, input_, textarea, ul, li,select,option, br, head, link
import json
from secrets import token_hex
app = Flask(__name__)
app.config['SECRET_KEY'] = token_hex(32)

restaurants = {}
preferences = []
@app.route('/', methods=["GET", "POST"])
def homepage():
    # from https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
    f = open("restaurant_catalog.json")
    restaurants = json.load(f)

    restaurant_name_list = [] 
    for i in restaurants.keys():
        restaurant_name_list.append(li(i))
    preferences_name_list = []
    for i in preferences:
        name = "" + i["maximum_price"]+ ", " + ", ".join(i["diet"])
        preferences_name_list.append(li(name))
    
    if request.method == 'POST':
        if "save_settings_btn" in request.form:
            session["restaurants"] = restaurants
            session["preferences"] = preferences
            session.modified = True
            #from https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
            with open("restaurant_catalog.json", "w+") as outfile:
                json.dump(restaurants, outfile)

    response = html(
        head(
            link(rel="stylesheet", href="static/restaurant_style.css")
        ),
        h1("Restaurant Finder"),
        p("Restaurants: "),
        body(
            ul(
                *restaurant_name_list
            )
        ),
        form(action="/add_restaurant")(               
            input_(type="submit", formaction= "/add_restaurant", name= "add_restaurant_btn", value = "Add")
        ), 
        p("Preferences: "),
        body(
            ul(
                *preferences_name_list
            )
        ),
        form(action="/add_preferences")(               
            input_(type="submit", formaction= "/add_preferences", name= "add_preference_btn", value = "Add")
        ),
        br,
        input_(type="submit", formaction="/", value="Save Restaurant/Preferences", name="save_btn"),
        br, br,
        form(action= "/find_restaurant")(
            input_(type="submit", formaction= "/display_recomendations", name= "find_restaurant_btn", value = "Find Best Restaurant")
        )
    )
    return str(response)
@app.route('/add_restaurant', methods=["POST"])
def add_restaurant():
    if request.method == 'POST':
        if "final_add_restaurant_btn" in request.form:
            if request.form["restaurant_name_tb"] != "" and request.form["price_group"] != "":
                option_list = []
                name = request.form["restaurant_name_tb"]
                price = request.form["price_group"]
                if request.form["options_tb"] != "":
                    option_list = request.form["options_tb"].split(", ")
                restaurants[name] = {"price_range": price, "options": option_list}
                with open("restaurant_catalog.json", "w+") as outfile:
                    json.dump(restaurants, outfile)
                return redirect("/")
    
    response = html(
        head(
            link(rel="stylesheet", href="static/restaurant_style.css")
        ),
        h1("Add Restaurant"),
        form(
            label("Restaurant Name: "),
            textarea(name="restaurant_name_tb", rows="1", cols="50"),
            p("Price Range:"),
            select(name = "price_group")(
                option("$"),
                option("$$"),
                option("$$$")
            ),
            p("Type in the restaurants dietary options separated by commas."),
            label("Dietary Options: "),
            textarea(name="options_tb", rows="1", cols="50"),
            br,br,
            input_(type="submit", name= "final_add_restaurant_btn", value = "Add Restaurant")
        )
    )
    return str(response)
@app.route('/add_preferences', methods=["POST"])
def add_preferences():
    if request.method == 'POST':
        if "final_add_preferences_btn" in request.form:
            if request.form["final_add_preferences_tb"] != "":
                option_list = []
                option_list = request.form["final_add_preferences_tb"].split(", ")
                preferences.append({"maximum_price": request.form["preference_price_group"], "diet":  option_list})
                return redirect("/")
    response = html(
        head(
            link(rel="stylesheet", href="static/restaurant_style.css")
        ),
        form(
            h1("Add Preferences"),
            p("Type in the restaurants dietary options separated by commas."),
            label("Dietary Preferences: "),
            textarea(name="final_add_preferences_tb", rows="1", cols="50"),
            p("Price Range:"),
            select(name = "preference_price_group")(
                option("$"),
                option("$$"),
                option("$$$")
            ),
            br,br,
            input_(type="submit", name= "final_add_preferences_btn", value = "Add Preferences")
        )
    )
    return str(response)
def suitable_restaurants(restaurants, preferences):
    possible_restaurants = []
    for rest_name, rest_details in restaurants.items():
        is_suitable = True
        for person in preferences:
            # Check price
            rest_price = rest_details["price_range"]
            pref_price = person["maximum_price"]
            if len(pref_price) < len(rest_price):
                is_suitable = False

            # Check diet
            rest_diet = rest_details["options"]
            pref_diet = person["diet"]
            # Need to check, for each item in pref_diet, it is in rest_diet
            for item in pref_diet:
                if item not in rest_diet:
                    is_suitable = False
        if is_suitable == True:
            possible_restaurants.append(rest_name)
    return possible_restaurants
@app.route('/display_recomendations', methods=["POST"])
def display_recommendations():
    final_restaurants = []
    final_restaurants_name_list = []
    final_restaurants.append(suitable_restaurants(restaurants, preferences))
    for i in final_restaurants:
        final_restaurants_name_list.append(li(i))
    if final_restaurants_name_list == []:
        response = html(
        head(
            link(rel="stylesheet", href="static/restaurant_style.css")
        ),
        h1("Recommendations!"),
        body(
            p("We could not find any suitable restaurants.")
        ),
    )
    else:
        response = html(
            head(
                link(rel="stylesheet", href="static/restaurant_style.css")
            ),
            h1("Recommendations!"),
            p("Here are the restaurants we recommend: "),
            body(
                ul(
                    *final_restaurants_name_list
                )
            ),
        )
    return str(response)
if __name__ == "__main__":
    app.run(debug=True)