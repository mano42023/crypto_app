# crypto_app

# Setup and installation

### Docker Build
Follow below steps to clone and build the docker imange for this project.
Make sure git and docker is installed in the system.

```sh
git clone https://github.com/mano42023/crypto_app.git

cd crypto_app/app

docker image build -t flask_docker .
```

### Docker run
Once image build successfully run the docker image using below command
application will run on port 5000. 
```sh
docker run -p 5000:5000 -d flask_docker
```

## Swagger UI
For accessing swagger UI open below link in the browser

http://127.0.0.1:5000/swagger/
