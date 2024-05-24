import asyncpg
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# PostgreSQL接続情報
DATABASE_URL = "postgresql://serenakurashina:Hajime34@localhost/postgres"

# 単語帳の単語モデル
class Word(BaseModel):
    word: str
    definition: str

# 単語を取得する
@app.get("/words/{word}", response_model=Word)
async def read_word(word: str):
    query = "SELECT * FROM words WHERE word = $1"
    row = await app.db_connection.fetchrow(query, word)
    if row:
        return {"word": row['word'], "definition": row['definition']}
    else:
        raise HTTPException(status_code=404, detail="Word not found")

# 新しい単語を追加する
@app.post("/words/", response_model=Word)
async def add_word(word: Word):
    query = "INSERT INTO words (word_registered, definition) VALUES ($1, $2) RETURNING word_registered, definition"
    row = await app.db_connection.fetchrow(query, word.word, word.definition)
    return {"word": row['word_registered'], "definition": row['definition']}

# ホームページの表示
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    # DB接続を非同期で開く
    connection = await asyncpg.connect(DATABASE_URL)
    # 全ての単語を取得
    words = await connection.fetch("SELECT word_registered, definition FROM words")
    # データベース接続の終了
    await connection.close()
    # 最初の単語のみを取得
    first_word = words[0] if words else None
    # テンプレートを処理してレスポンスする
    return templates.TemplateResponse("index.html", {"request": request, "word": first_word})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)