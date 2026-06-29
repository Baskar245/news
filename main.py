from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import cloudinary.uploader
import traceback

import cloudinary_config
from database import conn, cursor

app = FastAPI(
    title="News Portal API",
    version="1.0"
)

# CORS
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
        "message": "News Portal Backend Running Successfully"
    }


@app.post("/upload-news")
async def upload_news(
    news_date: str = Form(...),
    image: UploadFile = File(...)
):
    try:

        # Convert YYYY-MM-DD string to PostgreSQL DATE
        date_obj = datetime.strptime(news_date, "%Y-%m-%d").date()

        print("Uploading image...")

        # Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(image.file)

        image_url = upload_result["secure_url"]

        print("Cloudinary Success")

        # Save into PostgreSQL
        cursor.execute(
            """
            INSERT INTO news(news_date, image_url)
            VALUES(%s,%s)
            """,
            (date_obj, image_url)
        )

        conn.commit()

        print("Database Success")

        return {
            "success": True,
            "message": "News Uploaded Successfully",
            "image_url": image_url
        }

    except Exception as e:

        conn.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/news/{news_date}")
def get_news(news_date: str):

    try:

        date_obj = datetime.strptime(news_date, "%Y-%m-%d").date()

        cursor.execute(
            """
            SELECT id, news_date, image_url
            FROM news
            WHERE news_date=%s
            ORDER BY id
            """,
            (date_obj,)
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

    except Exception as e:

        conn.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/health")
def health():
    return {
        "status": "OK",
        "database": "Connected",
        "cloudinary": "Configured"
    }
