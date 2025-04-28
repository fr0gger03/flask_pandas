# Python, Pandas, Flask - Working with data using Pandas and Flask

This application grew out of a previous project - the <a href=https://github.com/vmware-archive/vmware-cloud-sizer-companion-cli>VMware Cloud Sizer Companion CLI.</a>  I am using several of the functions in that project to ingest an Excel file, perform some transformations on the data using Pandas, and return some basic statistics.

The entire application has been 'containerized' so I may experiment with pushing to the cloud in a standardized way, and leverage CI/CD.

### Building and running your application

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:5000.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)