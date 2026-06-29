import psycopg2

conn = psycopg2.connect(
    host="ep-cold-shape-apri4rwd.c-7.us-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_EMTo4ubGdWB8",
    port="5432",
    sslmode="require"
)

cursor = conn.cursor()