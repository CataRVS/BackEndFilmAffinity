# BackEndFilmAffinity
In the current digital era, where information and entertainment are just a click away, the overwhelming amount of content for movies and series available can be daunting. Sites like the popular Filmaffinity allow undecided users to discover new movies and rate them to help others in the same situation. Based on this, we have developed a project that mimics these key functionalities, combining the robustness and versatility of Django in the backend with the agility of React in the frontend, to offer a fluid and attractive user experience.

Our application allows users not only to access a small database of movies but also to interact with it dynamically. Users can filter movies according to their preferences, view specific details of each title, and contribute to the community with their own ratings and reviews. Additionally, the customized registration system enriches the experience, allowing each user to remember the reviews they have already made.

## Installation
Create a virtual environment and install the dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If problems with the requirements appear, please remove the following dependency from the requirements.txt file and try again:
```bash
psycopg2==2.9.9
```

If you have a windows and already have a .venv folder, you can activate it with the following command:
```bash
cd BackEnd
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Make sure that all migrations are up to date:
```bash
python manage.py makemigrations
python manage.py migrate
```

To run the server, execute the following command:
```bash
python manage.py runserver
```

To add data to the database, you can use the following command:
```bash
python fill_database.py
```

## Models
The application has the following models:
- **Movie**: Represents a movie with its title, date released, duration, synopsis, language actors, director, genres and posters
- **Review**: Represents a review made by a user to a movie, with a rating and a comment
- **User**: Represents a user with a email, password, name and surname
- **Categories**: Represents a category with a name
- **Director**: Represents a director with a name ad surname
- **Actor**: Represents an actor with a name and surname

## API
The application has the following endpoints presented in a table below:

| URL                                   | HTTP Methods          | Response Codes                                    | Functionality                                            |
|---------------------------------------|-----------------------|---------------------------------------------------|----------------------------------------------------------|
| `/movies/`                            | GET, POST             | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized | List or create movies                                    |
| `/movies/<int:pk>/`                   | GET, PUT, DELETE      | 200 OK, 204 No Content, 400 Bad Request, 401 Unauthorized, 404 Not Found | View, update, or delete a movie                          |
| `/users/`                             | POST                  | 201 Created, 400 Bad Request, 409 Conflict        | User registration                                        |
| `/users/login/`                       | POST                  | 201 Created, 401 Unauthorized                      | User login                                               |
| `/users/logout/`                      | DELETE                | 204 No Content, 401 Unauthorized                   | User logout                                              |
| `/users/info/`                        | GET, PUT, DELETE      | 200 OK, 204 No Content, 400 Bad Request, 401 Unauthorized | Get, update, or delete user information                  |
| `/users/check-session/`               | GET                   | 200 OK, 401 Unauthorized                           | Check if the user is logged in                           |
| `/users/check-admin/`                 | GET                   | 200 OK, 401 Unauthorized                           | Check if the user is an administrator                    |
| `/users/ratings/`                     | GET                   | 200 OK, 401 Unauthorized                           | List user's ratings                                      |
| `/movies/<int:pk>/rating/`            | GET, POST             | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 409 Conflict | List or create a rating for a movie                      |
| `/movies/<int:pk>/rating/user-rating/`| GET, PUT, DELETE      | 200 OK, 204 No Content, 400 Bad Request, 401 Unauthorized, 404 Not Found | Get, update, or delete a user's movie rating             |
| `/actors/`                            | GET, POST             | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized | List or create actors                                    |
| `/directors/`                         | GET, POST             | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized | List or create directors                                 |
| `/categories/`                        | GET, POST             | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized | List or create categories                                |

OpenAPI documentation can be created automatically by introducing the following direction in a navigator while the server is running:
`http://localhost:8000/schema/`
