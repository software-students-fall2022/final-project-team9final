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

def test_book_page(app_with_book):
    url='/book'
    app = app_with_book[0]
    id = app_with_book[1]
    response = app.post(url,data={'id':id})
    assert response.status_code == 200

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
    id = app_with_book[1]
    response = app.post(url,data={'username':"test",'storyId':id})
    assert response.status_code == 200

def test_updateLike(app_with_book):
    url='/api/updateLike'
    app = app_with_book[0]
    id = app_with_book[1]
    response = app.post(url,data={'username':"test",'storyId':id})
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
