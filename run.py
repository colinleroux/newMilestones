from deeds import create_app

app = create_app()
app.debug = True
if __name__ == '__main__':
    app.run(host='10.1.1.22',port='5000')
