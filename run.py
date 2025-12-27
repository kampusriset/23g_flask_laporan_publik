from app import create_app
from app.models import db

app = create_app()

@app.cli.command()
def initdb():
    db.create_all()
    print("Database tables created!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
