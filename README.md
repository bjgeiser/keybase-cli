# keybase-cli

[![Docker Build](https://github.com/bjgeiser/keybase-cli/actions/workflows/buildx.yaml/badge.svg)](https://github.com/bjgeiser/keybase-cli/actions/workflows/buildx.yaml)

Keybase docker container that exposes the keybase CLI and some common commands such as getting files or git loading github action secrets.

GitHub: https://github.com/bjgeiser/keybase-cli <br>
Docker Hub: https://hub.docker.com/r/bjgeiser/keybase-cli
## Usage

### Example Docker Command

```shell
docker run --rm \
   -v $PWD:$PWD -w $PWD \
   -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" \
   -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli keybase --version
```
## Environment Variables

| Environment Variable | Description                            | Required |
|----------------------|----------------------------------------|----------|
| KEYBASE_USERNAME     | Keybase user name                      | Yes      |
| KEYBASE_PAPERKEY     | Keybase paper key                      | Yes      |
| KEYBASE_UID          | Docker host user id to store files as  | No       |
| KEYBASE_GID          | Docker host group id to store files as | No       |

### About file permissions
By default keybase will copy files with the following permissions `-rw-------` and 
the keybase executable will not run as root.  Without setting `KEYBASE_UID` and `KEYBASE_GID` copied out files will be 
be owned by `1000:1000`. In order for your files to be readable, the calling user can pass the 
current user and group into the container with environment variables. The script can then dynamically create a user 
inside the container with the same `UID:GID` as the host user and files will be readable after the container exits.
Using `--user UID:GID` will not set up a user with a home directory (required for keybase) dynamically and the container will detect this and error out. 

## Commands

| Command               | syntax                                                                                                                                     | Description                                         |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| github-action-secrets | `github-action-secrets keybase://path/to/file`                                                                                             | For use in github actions<br>to get keybase secrets |
| get                   | `get keybase://path/to/file {localpath}`                                                                                                   | Get the file from keybase and copy to a local path  |
| read                  | `read keybase://path/to/file`                                                                                                              | Dump contents of file to stdout                     |
| clone                 | `clone {git clone options} keybase://path/to/repo {localpath}`                                                                             | Clone a keybase git repository                      |
| raw                   | See: [client command](https://book.keybase.io/docs/cli)                                                                                    | Run any keybase client command                      |
| batch                 | `batch "{any of the above commands},{any of the above commands}"` or<br> `batch "{any of the above commands};{any of the above commands}"` | Run more than 1 command in a single docker run      |
| file                  | `file /path/to/file`                                                                                                                       | Run more than 1 command in a single docker run                      |
> **Note**: `{arguments}` are optional.

### Command: `github-action-secrets`

----
```shell
docker run --rm \
   -v $PWD:$PWD -w $PWD \
   -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" \
   -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli github-action-secrets keybase://path/to/file
```
This command will parse a `.yaml`, `.json` or `.env` file and set secrets in a github action. Each entry result in the supplied file will cause the container to emit.<br> 
`::set-output name={name}::{value}` [reference](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter) <br> 
`::add-mask::{value}` [reference](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#masking-a-value-in-log)
>Note secrets loaded in using this method will be masked in with `*****` in workflow logs.  See: [reference](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) 
>for more information regarding action security.

#### Examples
`action-secrets.yaml`
```yaml
secret_1: this is secret 1
secret_2: this is secret 2
```
`action-secrets.json`
```json
{
  "secret_1": "this is secret 1",
  "secret_2": "this is secret 2"
}
```
`action-secrets.env`
```shell
secret_1="this is secret 1"
secret_2="this is secret 2"
secret_3=this_is_secret_3
```

#### Using in [github actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
````yaml
jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - name: Get secrets
        id: keybase_secrets
        shell: bash
        run: |
          run --rm \
           -v $PWD:$PWD -w $PWD \
           -e KEYBASE_USERNAME="${{secrets.KEYBASE_USERNAME}}" \
           -e KEYBASE_PAPERKEY="${{secrets.KEYBASE_PAPERKEY}}" \
           -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
            bjgeiser/keybase-cli github-action-secrets keybase://path/to/file 
      
      - name: Check that secret is loaded and masked
        ### This should log the secret with `*****`
        run: echo "${{steps.secrets.outputs.secret_1}}"
````

### Command: `get`

----
Copy a file to the local file system.
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli get keybase://path/to/file
```
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli get keybase://path/to/file keybase://path/to/file path/to/local/file
```
### Command: `read`

----
Print files to stdout.
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli read keybase://path/to/file
```
### Command: `clone`

----
Clone a git repository.
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli clone keybase://path/to/clone
```
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli clone -b my_branch keybase://path/to/clone path/to/local
```
### Command: `raw`

----
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli keybase --version
```
### Command: `batch`

----
Executes a series of commands in a `,` or `;` separated string.
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli batch "{any of the above commands},{any of the above commands}"`
```

### Command: `file`

----
Executes a series of commands contained in a yaml file.
```bash
docker run --rm -v $PWD:$PWD -w $PWD -e KEYBASE_USERNAME="$KEYBASE_USER" \
   -e KEYBASE_PAPERKEY="$KEYBASE_PAPERKEY" -e KEYBASE_UID=$UID -e KEYBASE_GID=$GID \
   bjgeiser/keybase-cli file keybase://path/to/command_file.yaml
```
`command_file.yaml`
```yaml
commands:
  - get keybase://path/to/file
  - get keybase://path/to/file2
  - get keybase://path/to/file3
  - clone keybase://path/to/clone
  - github-action-secrets keybase://path/to/file
```

