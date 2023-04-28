# Tests

## dbt sample project

In order to run tests on dbt artifacts that are as close to reality as possible, we have a sample dbt project inside
the `_fixtures` folder.

It uses a Postgres adapter to connect on a Postgres database provided in this repository through Docker.

Those steps are not necessary for running or writing new tests, but only when you need to update the artifacts generated.

### Updating the project

```shell
$ pip install "dbt~=0.21.0" 
```

Add the following entry in your dbt `~/.dbt/profiles.yaml`:

```shell
dbt_sample_project:
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5433
      user: postgres
      password: postgres
      dbname: dbt_sample_project
      schema: dev
      threads: 8

  target: dev
```

Go to the root folder of the dbt sample project before running the next commands. 

To spin up the database, open up a new terminal and run:

```shell
$ docker-compose up
```

And finally, test your connection by running:

```shell
$ dbt debug --target dev
```

As you confirm that connection could be established, you can proceed with your changes in the dbt project (e.g adding
new columns or documentation). After your changes in the dbt project are done, create the artifacts and copy
the `manifest` to a new file, since this is what the unit tests are expecting.

Note: we use `jq` to prettify the JSON files. This tool needs to be installed separately (eg: throw `brew`). For the
command below, we need a temporary file because it's not possible to directly redirect the output to the same file we
are reading.

```shell
$ dbt run
$ dbt docs generate
$ cat target/catalog.json  | jq '.' | cat > target/catalog.json.tmp && mv target/catalog.json.tmp target/catalog.json
$ cat target/manifest.json | jq '.' | cat > target/manifest.json.tmp && mv target/manifest.json.tmp target/manifest.json
$ cp target/manifest.json target/manifest_original.json
```

Another advantage of copying the file to a new name is that you can now run our project while still preserving the
original manifest.

```shell
$ python -m dbttoolkit.documentation.actions.propagate \
  --artifacts-folder=./target \
  --input-manifest-filename=manifest_original.json \
  --output-manifest-path=./target/manifest.json
```

And finally, you can spin up the dbt docs server to inspect the modified manifest.

```shell
$ dbt docs serve
```

After you are done, note that `Ctrl+c` will stop the Postgres container but not its network and storage. For a complete
tear down of the `docker-compose`, run:

```shell
$ docker-compose down
```

### Initial setup

Those are the commands used to set up the sample project. You do not need to run it when updating the sample project.

```shell
$ dbt init dbt_sample_project
```
