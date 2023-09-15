from fastapi import FastAPI, Body, Path, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()
app.title = "Mi aplicacion con FastAPI"
app.version = "0.0.1"

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

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Hello World</h1>')

@app.get('/movies', tags=['movies'])
def get_movies():
    return movies

@app.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    for item in movies:
        if item["id"] == id:
            return item
    return "No existen peliculas con este código"

@app.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    '''mi solucion al reto de retornar peliculas por categoría'''
    """accu = []
    for item in movies:
        if item["category"] == category:
            accu.append(item)
    return accu"""
    '''solucion del profe para el reto de peliculas por categoría'''
    return [item for item in movies if item["category"] == category]

@app.post('/movies', tags=['movies'])
def create_movie(movie: Movie):
    movies.append(movie)
    return movies

@app.put('/movies/{id}', tags=['movies'])
def modify_movie(id: int, movie: Movie):
    for item in movies:
        if item["id"] == id:
            item["title"] = movie.title
            item["overview"] = movie.overview
            item["year"] = movie.year
            item["rating"] = movie.rating
            item["category"] = movie.category
        return movies
    return "No existe el id indicado"

@app.delete('/movies/{id}', tags=['movies'])
def delete_movie(id: int):
    for item in movies:
        if item["id"] == id:
            movies.remove(item)
            return movies
    return movies

