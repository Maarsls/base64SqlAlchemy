from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api
from sqlalchemy import Column, Integer, Text, Float, DateTime, create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from flask_restful import Resource, Api
from dataclasses import dataclass
import json

app = Flask(__name__)  # Die Flask-Anwendung
api = Api(app)  # Die Flask API

Base = declarative_base()  # Basisklasse aller in SQLAlchemy verwendeten Klassen
metadata = Base.metadata

# Welche Datenbank wird verwendet
engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=engine))
Base.query = db_session.query_property()
app = Flask(__name__)  # Die Flask-Anwendung
api = Api(app)  # Die Flask API


@dataclass  # Diese ermoeglicht das Schreiben als JSON mit jsonify
class BinaryWithMetadata(Base):
    __tablename__ = 'binary_with_metadata'
    id: int
    name: str
    ext: str
    data: str
    desc: str
    when: str

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    ext = Column(Text)
    data = Column(Text)
    desc = Column(Text)
    when = Column(DateTime, default=func.now())


class BinaryWithMetadataREST(Resource):
    def get(self, id):
        info = BinaryWithMetadata.query.get(id)
        if info is None:
            return jsonify({'message': 'object with id %d does not exist' % id})
        return jsonify(info)

    def put(self, id):
        d = request.get_json(force=True)
        print(d)
        info = BinaryWithMetadata(
            name=d['name'], ext=d['ext'], data=d['data'], desc=d['desc'])

        db_session.add(info)
        db_session.flush()
        print(info.id)
        return jsonify(info)
    
    def delete(self, id):
        info = BinaryWithMetadata.query.get(id)
        if info is None:
            return jsonify({'message': 'object with id %d does not exist' % id})
        db_session.delete(info)
        db_session.flush()
        return jsonify({'message': '%d deleted' % id})



api.add_resource(BinaryWithMetadataREST, '/img_meta/<int:id>')

@app.route('/search/<string:query>')
def getQuestionsRoute(query):
    res = BinaryWithMetadata.query.filter(or_(BinaryWithMetadata.name.contains(query), BinaryWithMetadata.desc.contains(query))).all()
    return jsonify(res)

@app.teardown_appcontext
def shutdown_session(exception=None):
    print("Shutdown Session")
    db_session.remove()


def init_db():
    # Erzeugen der Tabellen für die Klassen, die oben deklariert sind (muss nicht sein, wenn diese schon existiert)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
