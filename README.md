# Python, Pandas, Flask - Working with data using Pandas and Flask

This application grew out of a previous project - the <a href=https://github.com/vmware-archive/vmware-cloud-sizer-companion-cli>VMware Cloud Sizer Companion CLI.</a>  I am using several of the functions in that project to ingest an Excel file, perform some transformations on the data using Pandas, and return some basic statistics.

The entire application has been 'containerized' so I may experiment with pushing to the cloud in a standardized way, and leverage CI/CD.

### Create Environment-Specific Files

- [ ] Copy current envs/`.env.template` as starting point
- [ ] Document all environment variables with comments
- [ ] Use placeholder values like `your-secret-here`
- [ ] Include sections for: Flask, Database, Security, File Upload, Logging, Performance

Create two environment files:

**File: `envs/local.env`**
- Development settings
- Can include dev secrets (gitignored)
- Use localhost/docker service names
- Debug mode enabled

**File: `envs/production.env`**
- Production settings
- Use a secret manager for secrets
- Debug mode disabled
- Production database URLs

### Building and running your application - development

When you're ready, start your application by running:
`docker compose --env-file envs/local.env up --build`

This will use env/local.env to set all required environmental variables for local development.  

**Note:** the `compose.override.yaml` file will automatically be used to update the default `compose.yaml` file.

If you would optionally like to leverage compose watch for interactive use / troubleshooting of the application while you are working on it, then use:
`docker compose --env-file envs/local.env watch`

(watch may not be used with `up` or `--build`)

Your application will be available at http://localhost.

### Building and running your application - production

When you're ready, start your application by running:
`docker compose --env-file envs/production.env up --build`

This will use env/production.env to set all required environmental variables for your production configuration.  

Your application will be available at http://localhost.

### Tear-down
You can use one of the following commands to tear down your containers:
`docker compose --env-file envs/local.env down -v`
or
`docker compose --env-file envs/production.env down -v`

