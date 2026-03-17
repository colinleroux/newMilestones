import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True  # TLS is not used with SSL
    MAIL_USE_SSL = False  # Enable SSL
    MAIL_USERNAME = '89390d001@smtp-brevo.com' #os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = 'QWj2Z8CX4hT75v63' #os.environ.get('EMAIL_PASS')
    SECRET_ACCESS_CODE = '2911'
    WTF_CSRF_ENABLED = True  # Enable CSRF protection
    WTF_CSRF_SECRET_KEY = 'your-secret-key'  # This can be any secret key
