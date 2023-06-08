import app

app = app.create_app()

if __name__ == '__main__':
    app.run(port=5050, debug=True)