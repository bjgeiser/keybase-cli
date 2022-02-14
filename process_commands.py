import os
import sys
import yaml
import json
import re
import subprocess

def execute_command(commands, show=False, echo=True):

    if echo:
        print(f"Executing command: {' '.join(map(str, commands))}")

    p = subprocess.run(commands, capture_output=True, text=True)
    if show:
        for l in p.stdout.splitlines():
            print(l)
        for l in p.stderr.splitlines():
            print(l)
    return p.stdout

def keybase_read_file(fileName):
    return execute_command(["keybase", "fs", "read", fileName])

def execute_github_action_secrets(fileName):
    if fileName.startswith("keybase://"):
        ext = os.path.splitext(fileName)[-1].lower()

        f = keybase_read_file(fileName)

        if ext == ".json":
            secrets = json.loads(f)
        elif ext == ".yaml" or ext == ".yml":
            secrets = yaml.safe_load(f)
        else:
            secrets = {}
            lines = f.splitlines()
            for l in lines:
                if "=" in l:
                    split = l.split("=", 1)
                    if "\"" == split[1][0] or "\'" == split[1][0]:
                        secret = re.sub(' #.*', '', split[1])
                        secret = secret.strip()
                        secret = secret[1:-1]
                    else:
                        secret = split[1].strip()

                    secrets[split[0]] = secret

    # itterate through all the secrets
    for attribute, value in secrets.items():
        if " " in attribute:
            print(f"Cannot set {attribute} because it contains spaces")
        else:
            print(f"::add-mask::{value}")
            print(f"::set-output name={attribute}::{value}")
            print(f"Secret set for: {attribute}")


def process_command(command):

    if "github-action-secrets" == command[0]:
        execute_github_action_secrets(command[1])
    elif "keybase" == command[0]:
        output = execute_command(command, show=True, echo=False)
        
    elif "get" == command[0]:
        fileName = command[1]
        if len(command) > 2:
            to = command[2]
            permission_fix = to
        else:
            to = "."
            permission_fix = os.path.basename(fileName)
        if fileName.startswith("keybase://"):
            print(f"Fetching: {fileName}")
            command = ["keybase", "fs", "cp", fileName, to]
            output = execute_command(command, show=True)
            command = ["chmod", "-R", "a+rw", permission_fix]
            output = execute_command(command, show=True)
    elif "clone" == command[0]:
        command = ["git"] + command
        output = execute_command(command, show=True)
    else:
        execute_command(command, show=True)

if __name__ == '__main__':

    command = sys.argv[1:]
    if command[0] == "batch":
        print("Parse and process commands")
        commands = command[1].split(",")
        if len(commands) == 1:
            commands = command[1].split(";")

        for c in commands:
            process_command(c.strip().split(" "))

    elif command[0] == "file":
        print("Parse and process commands")
        filename = command[1]
        if os.path.exists(filename):
            with open(filename) as f:
                ext = os.path.splitext(filename)[1]
                if ext == ".yaml" or ext == "yml":
                    commands = yaml.safe_load(f)
                elif ext == ".json":
                    commands = json.loads(f)

                for c in commands["commands"]:
                    process_command(c.split(" "))
        else:
            print(f"File: {filename} does not exist")
            exit(1)
    else:
        process_command(command)


