from flask import Flask, jsonify, send_from_directory, request
from tracker.satallites import *


tle = get_tle_data()
categories = ['all', 'starlink', 'ISS', 'GPS']
pos_cache = {cat: get_all_positions(cat) for cat in categories}
tree_cache = {cat: get_kd_tree(pos_cache[cat]) for cat in categories}

app = Flask(__name__, static_folder='../static')

@app.route('/')
def index():
    return send_from_directory('../static', "index.html")


@app.route('/nearest')
def nearest():
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))

    category = request.args.get('category', 'all')
    if category in pos_cache:
        sat = tree_search(tree_cache[category], pos_cache[category], lat, lng)
    else:
        pos = get_all_positions(category)
        sat = tree_search(get_kd_tree(pos), pos, lat, lng)

    return jsonify(sat)


@app.route('/satellites')
def get_satalites():
    category = request.args.get('category', 'all')
    return jsonify(get_all_positions(category))


if __name__ == "__main__":
    use_reloader=False
    app.run(debug=True)