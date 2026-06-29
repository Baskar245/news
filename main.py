from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cloudinary.uploader
import traceback

import cloudinary_config
from database import conn, cursor

app = FastAPI(
    title="News Portal API",
    version="1.0"
)

# Allow Flutter/Web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "News Archive Backend Running Successfully"
    }


@app.post("/upload-news")
async def upload_news(
    news_date: str = Form(...),
    image: UploadFile = File(...)
):
    try:

        print("========== NEW UPLOAD ==========")
        print("Date:", news_date)
        print("Image:", image.filename)

        # Upload image to Cloudinary
        result = cloudinary.uploader.upload(image.file)

        image_url = result["secure_url"]

        print("Cloudinary Upload Success")
        print(image_url)

        # Save into PostgreSQL
        cursor.execute(
            """
            INSERT INTO news(news_date, image_url)
            VALUES(%s,%s)
            """,
            (news_date, image_url)
        )

        conn.commit()

        print("Database Insert Success")

        return {
            "success": True,
            "message": "News Uploaded Successfully",
            "image_url": image_url
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/news/{news_date}")
def get_news(news_date: str):

    try:

        cursor.execute(
            """
            SELECT id, news_date, image_url
            FROM news
            WHERE news_date=%s
            ORDER BY id
            """,
            (news_date,)
        )

        rows = cursor.fetchall()

        news = []

        for row in rows:
            news.append(
                {
                    "id": row[0],
                    "date": str(row[1]),
                    "image_url": row[2]
                }
            )

        return news

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/health")
def health():
    return {
        "status": "Backend Running",
        "database": "Connected"
    }
