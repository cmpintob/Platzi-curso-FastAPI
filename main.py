from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Any, Coroutine, Optional, List
from jwt_manager import create_token, validate_token
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()
app.title = "Mi aplicacion con FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Las credenciales son invalidas")

class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2023)
    rating: float = Field(gt=0, le=10.0)
    category: str = Field(min_length=5, max_length=15)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "My movie",
                "overview": "Description of my movie",
                "year": 2023,
                "rating": 9.2,
                "category": "Horror"
            }
        }

movies = [
    {
		"id": 1,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Acción"
	},
    {
		"id": 2,
		"title": "Avatar",
		"overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
		"year": "2009",
		"rating": 7.8,
		"category": "Acción"
	}
]

@app.get('/', tags=['home'], status_code=200)
def message():
    return HTMLResponse('<h1>Hello World</h1>')

@app.post('/login', tags=['auth'])
def login(user:User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token : str = create_token(user.dict())
        return JSONResponse(status_code = 200, content=token)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
    """actualizacion de la consulta con base de datos"""
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={'nessage':"Pelicula no encontrada"})
    return JSONResponse(status_code=200, content=jsonable_encoder(result))
    """Solucion anterior local"""
    """for item in movies:
        if item["id"] == id:
            return JSONResponse(status_code=200, content=item)
    return JSONResponse(status_code=404, content=[])"""

@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
    '''Version con base de datos'''
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not result:
        return JSONResponse(status_code=404, content={'nessage':"Pelicula no encontrada"})
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

    '''Caso desactualizado'''
    '''mi solucion al reto de retornar peliculas por categoría'''
    """accu = []
    for item in movies:
        if item["category"] == category:
            accu.append(item)
    return accu"""
    '''solucion del profe para el reto de peliculas por categoría'''
    """
    data = [item for item in movies if item["category"] == category]
    return JSONResponse(status_code=200, content=data)
    """
    
@app.post('/movies', tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    '''modelo con base de datos'''
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    '''modelo inicial con archivos de texto y clases internas'''
    '''movies.append(movie)'''
    return JSONResponse(status_code=201, content={"Response": "Pelicula Creada"})

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def modify_movie(id: int, movie: Movie) -> dict:
    """actualizacion con base de datos"""
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"Response": "No existen peliculas con el ID indicado"})
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
    return JSONResponse(status_code=200, content={"Response": "Su pelicula ha sido actualizada"})
    """formato local anterior"""
    """
    for item in movies:
        if item["id"] == id:
            item["title"] = movie.title
            item["overview"] = movie.overview
            item["year"] = movie.year
            item["rating"] = movie.rating
            item["category"] = movie.category
            return JSONResponse(status_code=200, content={"Response": "Su pelicula ha sido actualizada"})
    return JSONResponse(status_code=404, content={"Response": "No existen peliculas con el ID indicado"})
    """

@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int) -> dict:
    """actualizacion con base de datos"""
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"Response": "No existen peliculas con el ID indicado"})
    db.delete(result)
    db.commit()
    return JSONResponse(status_code=200, content={"Response": "Pelicula eliminada satisfactoriamente"})
    """Formato local anterior"""
    """
    for item in movies:
        if item["id"] == id:
            movies.remove(item)
            return JSONResponse(status_code=200, content={"Response": "Pelicula eliminada exitosamente"})
    return JSONResponse(status_code=404, content={"Response": "No existen peliculas con el ID indicado"})
    """
