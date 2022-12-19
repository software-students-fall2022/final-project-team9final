def test_story_page(flask_app):
    url='/'
    response = flask_app.get(url, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/stories'
    url='/stories'
    response = flask_app.get(url)
    assert response.status_code == 200

def test_login_page(app_with_data):
    url='/login'
    response = app_with_data.get(url)
    assert response.status_code == 200

def test_login(app_with_data):
    url='/login'
    response = app_with_data.get(url, query_string={'username': 'test', 'password':'test'}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path=='/stories'

def test_create_book_page(app_with_data):
    url='/create-book'
    response = app_with_data.get(url)
    assert response.status_code == 200

# Should work if you give it the api key
# def test_book_page(app_with_book):
#     url='/book'
#     app = app_with_book[0]
#     id = app_with_book[1]
#     response = app.post(url,data={'id':id})
#     assert response.status_code == 200

def test_private(app_with_book):
    url='/private'
    app = app_with_book[0]
    response = app.get(url)
    assert response.status_code == 200

def test_share(app_with_book):
    url='/share'
    app = app_with_book[0]
    id = app_with_book[1]
    response = app.post(url,data={'id':id})
    assert response.status_code == 200

def test_unshare(app_with_book):
    url='/unshare'
    app = app_with_book[0]
    id = app_with_book[1]
    response = app.post(url,data={'id':id})
    assert response.status_code == 200

def test_countLike(app_with_book):
    url='/api/countLike'
    app = app_with_book[0]
    id = str(app_with_book[1])
    response = app.post(url,json={"username":"test","storyID":id})
    assert response.status_code == 200

def test_updateLike(app_with_book):
    url='/api/updateLike'
    app = app_with_book[0]
    id = str(app_with_book[1])
    response = app.post(url,json={'username':"test",'storyID':id})
    assert response.status_code == 200

def test_delete(app_with_book):
    url='/delete'
    app = app_with_book[0]
    id = app_with_book[1]
    response = app.post(url,data={'id':id})
    assert response.status_code == 200

def test_logout(app_with_data):
    url='/logout'
    response = app_with_data.get(url, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/stories'

def test_register_page(app_with_database):
    url='/register'
    response = app_with_database.get(url)
    assert response.request.path == '/register'
    assert response.status_code == 200

def test_register(app_with_database):
    url='/register'
    response = app_with_database.post(url, data={'username': 'Santa Claus', 'firstName': 'Santa', 'lastName': 'Claus', 'password':'Christmas'},follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path=='/login'
    response = app_with_database.get(response.request.path, query_string={'username': 'Santa Claus', 'password': 'Christmas'}, follow_redirects = True)
    assert response.status_code == 200
    assert response.request.path == '/stories'

def test_profile(app_with_followers):
    url='/profile'
    app = app_with_followers[0]
    # id = app_with_followers[1]
    response = app.post(url, data={'id': 'test'})
    assert response.status_code == 200

def test_follow(app_with_book):
    url='/follow'
    app = app_with_book[0]
    db = app_with_book[2]
    response = app.post(url, data={'id': 'Santa Claus', 'c_username': 'test'})
    assert response.status_code == 200
    user = db.find_one('users',{"username" : 'test'})
    followers = list(user["followers"])
    following = list(user["following"])
    assert len(followers) == 0
    assert len(following) == 1

def test_unfollow(app_with_followers):
    url='/unfollow'
    app = app_with_followers[0]
    db = app_with_followers[1]

    response = app.post(url, data={'id': 'bar', 'c_username': 'foo'})
    assert response.status_code == 200

    user = db.find_one('users',{"username" : 'foo'})
    followers = list(user["followers"])
    following = list(user["following"])

    user2 = db.find_one('users', {'username': 'bar'})
    followers2 = list(user2['followers'])
    following2 = list(user2['following'])

    assert len(followers) == 0
    assert len(following) == 0
    assert len(followers2) == 0
    assert len(following2) == 0