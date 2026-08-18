import app as application
with application.app.app_context():
    application.db.create_all()
    print("Tables created successfully in Supabase!")
