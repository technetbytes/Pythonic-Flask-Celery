from app import factory
import app

if __name__ == "__main__":
    app = factory.create_app(celery=app.celery)
    app.run(host='192.168.100.9',port=5000)