from app import app

if __name__ != "__main__":
    import gunicorn
    app.run()
