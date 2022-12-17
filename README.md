![web-app](https://github.com/software-students-fall2022/final-project-team9final/actions/workflows/build.yaml/badge.svg)

## Introduction

This web application allows users to create stories based on a random prompt given by the users. The created stories can be saved in individual personalized collections or be shared for other users to read and like. An image is created on demand for each paragraph of a story, creating a storybook-like reading experience.

## SetUp

1. An `.env` folder is required in the `web-app` directory. 
    - There is a total of 3 variables that needs to be included
        - `MONGO_DBNAME`
        - `MONGO_URI`
        - `OPENAI_API_KEY`
            - Our program uses `OPENAI` API to create the story images and the story itself.
            - To use the OPENAI features, an account can be created at their main websited (https://openai.com/api/).
            - OPENAI provides users with free credits to utilize its features.
2. Flask login is used for access, thus in order to access the functionalities of the app, an account must be created after running the project.

## Run the Project

1. The current port that the containers use for the app is 5000. Verify that no other app is running on that port before running the project.
2. At the root folder of the project run using the command `docker compose up`
3. Head to [localhost](http://127.0.0.1:5000/) to register as a new user
4. After registration log in to experience all the functionality of the application.

## Run the Project Without Containers
1. Move to the `web-app` folder using `cd` command
2. Run using the command
```
flask run
```

## Run Tests
- At the `web-app` directory of the project run the commands

```(python)
python -m pytest
```

2. To test for `coverage` run the command
```
coverage run -m pytest ./tests/*.py
```

## Authors
- Brandon Chen: [Github](https://github.com/b-chen00)
- Adam Sidibe: [Github](https://github.com/sidibee)
- Alexander Chen: [Github](https://github.com/TheAlexanderChen)
- John Kolibachuk: [Github](https://github.com/jkolib)
- Seok Tae Kim: [Github](https://github.com/seoktaekim)
