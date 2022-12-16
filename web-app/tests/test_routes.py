def test_story_page(flask_app):
    url='/'
    response = flask_app.get(url, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/stories'
    url='/stories'
    response = flask_app.get(url)
    assert response.status_code == 200

# def test_login_page(app_with_data):
#     url='/login'
#     response = app_with_data.get(url)
#     assert response.status_code == 200
#
# def test_login(app_with_data):
#     url='/login'
#     response = app_with_data.get(url, query_string={'username': 'test', 'password':'test'}, follow_redirects=True)
#     assert response.status_code == 200
#     assert response.request.path=='/stories'
#
# def test_logout(app_with_data):
#     url='/logout'
#     response = app_with_data.get(url, follow_redirects=True)
#     assert response.status_code == 200
#     assert response.request.path == '/stories'
#
# def test_register_page(app_with_database):
#     url='/register'
#     response = app_with_database.get(url)
#     assert response.request.path == '/register'
#     assert response.status_code == 200
#
# def test_register(app_with_database):
#     url='/register'
#     response = app_with_database.post(url, data={'username': 'Santa Claus', 'firstName': 'Santa', 'lastName': 'Claus', 'password':'Christmas'},follow_redirects=True)
#     assert response.status_code == 200
#     assert response.request.path=='/login'
#     response = app_with_database.get(response.request.path, query_string={'username': 'Santa Claus', 'password': 'Christmas'}, follow_redirects = True)
#     assert response.status_code == 200
#     assert response.request.path == '/stories'
