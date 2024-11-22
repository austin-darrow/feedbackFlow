push:
	git add . && git commit -m "update" && git push heroku main

log:
	heroku logs --tail