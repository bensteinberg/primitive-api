# primitive-api

This is a minimal Flask API for running
[primitive](https://github.com/fogleman/primitive) in Docker, for
possible use in Dokku.

Build with

	docker build -t primitive-api .
	
Run with

    docker run -it -p 8081:8000 primitive-api
	
Try it out with

    curl -F "file=@<somefile.png>" http://localhost:8081/

The output is JSON; the value of `img` is an `img` tag for
interpolation in HTML.
