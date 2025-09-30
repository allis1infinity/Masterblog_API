from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def find_post_by_id(post_id: int):
    """ Searches for a post by its ID. Returns the post object or None. """
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


def validate_post_data(data):
    """ Checks for required fields for creating a post (title and content). """
    if "title" not in data or "content" not in data:
        return False
    return True


@app.route('/api/posts', methods=['GET', 'POST'])
def list_and_create_posts():
    """Handles listing all posts (GET) and creating a new one (POST)."""
    if request.method == 'GET':
        sort_field = request.args.get('sort')
        direction = request.args.get('direction', 'asc')

        posts = POSTS[:]  # Create a copy for safe sorting

        # Apply sorting logic
        if sort_field:
            if sort_field not in ["title", "content"]:
                return jsonify({"error": "Invalid sort parameter. Please use 'title' or 'content'."}), 400
            if direction not in ["asc", "desc"]:
                return jsonify({"error": "Invalid direction parameter. Direction must be either 'asc' or 'desc'."}), 400

            reverse = True if direction == "desc" else False
            # Case-insensitive sorting
            posts = sorted(posts, key=lambda x: x[sort_field].lower(),
                           reverse=reverse)

        return jsonify(posts)


    elif request.method == 'POST':
        data = request.get_json()

        if not data or not validate_post_data(data):
            return jsonify({'error': 'Title and content are required'}), 400

        # Generate new ID
        new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
        new_post = {
            "id": new_id,
            "title": data["title"],
            "content": data["content"]
        }

        POSTS.append(new_post)
        return jsonify(new_post), 201

    return jsonify({"error": "Method Not Allowed"}), 405


@app.route('/api/posts/<int:post_id>', methods=['PUT', 'DELETE'])

def update_delete_post(post_id):
    """Handles updating an existing post (PUT) or deleting a post (DELETE) by ID."""
    post = find_post_by_id(post_id)

    if post is None:
        return jsonify({"error": "Not Found"}), 404

    if request.method == 'PUT':
        new_data = request.get_json()

        if not new_data:
            return jsonify({"error": "No data provided"}), 400

        post.update(new_data)

        return jsonify(post), 200

    elif request.method == 'DELETE':
        POSTS.remove(post)
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

    return jsonify({"error": "Method Not Allowed"}), 405


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Searches posts by title or content."""
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = []
    for post in POSTS:
        title_search = title_query in post[
            "title"].lower() if title_query else False
        content_search = content_query in post[
            "content"].lower() if content_query else False

        if title_search or content_search:
            results.append(post)

    return jsonify(results), 200


@app.errorhandler(404)
def not_found_error(_):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(_):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)