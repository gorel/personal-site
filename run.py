import personal_site

app = personal_site.create_app()
app.run(
    host=app.config["SERVER_HOST"],
    port=app.config["SERVER_PORT"],
    debug=app.config["DEBUG"],
    threaded=True,
)
