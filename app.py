# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

# подключаем приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#создаем модель фильмов
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


# создаем модель режиссера
class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# создаем модель жанра
class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# создаем скему для сериализации/десериализации
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Str()
    director = fields.Str()


# создаем скему для сериализации/десериализации
class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# создаем скему для сериализации/десериализации
class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


# готовим сериализаторы для единичных и множественных итераций
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

# создаем API
api = Api(app)

#создаем неймспейсы
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    """
    Создаем вьюшку для фильмов
    """
    def get(self):
        """
        Функция, которая выполняет запрос GET и выводит все фильмы, если нет доп. условий в запросе
        """

        all_movies = db.session.query(Movie)

        # если в запросе есть director_id, то вывод будет только с теми фильмами, у которых соответствует director_id
        director_id = request.args.get('director_id')
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)

        # если в запросе есть genre_id, то вывод будет только с теми фильмами, у которых соответствует genre_id
        genre_id = request.args.get('genre_id')
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(all_movies.all()), 200

    def post(self):
        """
        Функция, которая выполняет запрос POST и добавляет новый фильм в БД
        """

        req_json = request.json
        new_movie = Movie(**req_json)

        db.session.add(new_movie)
        db.session.commit()

        return "New movie added!", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    """
    Создаем вьюшку, для фильма с конкретным id
    """
    def get(self, mid: int):
        """
        Функция, которая выполняет запрос GET и выводит фильм с конкретным id
        """

        # если фильма с таким id не существует, то выдаст ошибку
        try:
            movie = db.session.query(Movie).filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return str(e), 404

    def put(self, mid: int):
        """
        Функция, которая выполняет запрос PUT и обновляет данные о фильме с конкретным id
        """

        movie = db.session.query(Movie).get(mid)
        req_json = request.json

        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.rating = req_json.get('rating')
        movie.genre = req_json.get('genre')
        movie.year = req_json.get('year')
        movie.director = req_json.get('director')
        movie.trailer = req_json.get('trailer')

        db.session.add(movie)
        db.session.commit()

        return f"Movie #{mid} updated!", 204

    def delete(self, mid: int):
        """
        Функция, которая выполняет запрос DELETE и удаляет данные о фильме с конкретным id
        """
        movie = db.session.query(Movie).get(mid)

        db.session.delete(movie)
        db.session.commit()

        return f"Movie #{mid} deleted successfully!", 204


@director_ns.route('/')
class DirectorsView(Resource):
    """
    Создаем вьюшку для режиссеров
    """
    def get(self):
        """
        Функция, которая выполняет запрос GET и выводит всех режиссеров в формате JSON
        """

        all_directors = db.session.query(Director).all()

        return directors_schema.dump(all_directors), 200

    def post(self):
        """
        Функция, которая выполняет запрос POST и добавляет в БД нового режиссера
        """

        req_json = request.json
        new_director = Director(**req_json)

        db.session.add(new_director)
        db.session.commit()

        return "New director added!", 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    """
    Создаем вьюшку для режиссера с конкретным id
    """
    def get(self, did: int):
        """
        Функция, котороая выполняет GET запрос и выводит режиссера с конкретным id
        """

        # если режиссер с указанным в запросе id не существует, выдаст ошибку
        try:
            director = db.session.query(Director).filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return str(e), 404

    def put(self, did: int):
        """
        Функция, которая обновляет данные о режиссера с конкретным id
        """

        director = db.session.query(Director).get(did)
        req_json = request.json

        director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()

        return f"Director #{did} updated successfully!", 204

    def delete(self, did: int):
        """
        Функция, которая удаляет данные о режиссера из БД с конкретным id
        """

        director = db.session.query(Director).get(did)

        db.session.delete(director)
        db.session.commit()

        return f"Director #{did} deleted successfully!", 204


@genre_ns.route('/')
class GenresView(Resource):
    """
    Создаем вьюшку для жанров
    """
    def get(self):
        """
        Функция, которая выполняет запрос GET и выводит все жанры
        """

        all_genres = db.session.query(Genre).all()

        return genres_schema.dump(all_genres), 200

    def post(self):
        """
        ФункциЯ, которая выполняет запрос POST и добавляет в БД новый жанр
        """

        req_json = request.json
        new_genre = Genre(**req_json)

        db.session.add(new_genre)
        db.session.commit()

        return "New genre added!", 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    """
    Создаем вьюшку для жанра с конкретным id
    """
    def get(self, gid: int):
        """
        Функция, которая выполняет запрос GET и выводит жанр с конкретным id
        """

        # если жанр с указанным id не существует - выдаст ошибку
        try:
            genre = db.session.query(Genre).filter(Genre.id == gid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return str(e), 404

    def put(self, gid: int):
        """
        Функция, которая выполняет запрос PUT и обновляет данные о жанре с конкретным id
        """

        genre = db.session.query(Genre).get(gid)
        req_json = request.json

        genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return f"Genre #{gid} updated successfully!", 204

    def delete(self, gid: int):
        """
        Функция, которая удалет информация о конкретном жанре по id из БД
        """

        genre = db.session.query(Genre).get(gid)

        db.session.delete(genre)
        db.session.commit()

        return f"Genre #{gid} deleted successfully!", 204


# запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
