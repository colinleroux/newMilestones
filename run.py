from deeds import create_app

app = create_app()
app.debug = True
if __name__ == '__main__':
    app.run(host='192.168.20.10',port='5000')
