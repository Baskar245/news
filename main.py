from fastapi import FastAPI, UploadFile, File, Form
import cloudinary.uploader

import cloudinary_config
from database import conn, cursor

app = FastAPI()


@app.get("/")
def home():
    return {"message": "News Archive Backend Running"}


@app.post("/upload-news")
async def upload_news(
    news_date: str = Form(...),
    image: UploadFile = File(...)
):
    result = cloudinary.uploader.upload(image.file)

    image_url = result["secure_url"]

    cursor.execute(
        """
        INSERT INTO news(news_date, image_url)
        VALUES(%s, %s)
        """,
        (news_date, image_url)
    )

    conn.commit()

    return {
        "message": "News Uploaded Successfully",
        "image_url": image_url
    }


@app.get("/news/{news_date}")
def get_news(news_date: str):

    cursor.execute(
        """
        SELECT id, news_date, image_url
        FROM news
        WHERE news_date = %s
        ORDER BY id
        """,
        (news_date,)
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "date": str(row[1]),
            "image_url": row[2]
        })

    return result