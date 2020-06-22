# Odoo Compare 

Flask application that shows deltas between Active Directory and Odoo. 

# Build and Run 

```sh
# in root directory 
$ docker build . --build-arg APP_ENV=production -t whatevertagyoulike:latest
$ docker run -p 8080:80 whatevertagyoulike
```

Then navigate to localhost:8080 on your machine

## License

Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [MIT License](LICENSE).
