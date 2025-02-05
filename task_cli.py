import json
import os.path
import sys
from argparse import ArgumentParser
from datetime import datetime
from typing import Callable, Literal, Generator

from tabulate import tabulate


def main() -> None:
    database_path = os.path.expanduser("tasks.json")
    load_database(database_path)

    supported_queries: dict[str, dict] = get_supported_queries()

    query, args = get_query(supported_queries)

    database: dict[str,dict] = load_database(database_path)

    try:
        query(database, **args)
    except KeyError:
        sys.exit("No task found")
    save_database(database,database_path)


def load_database(path: str) -> dict[str,dict]:
    try:
        with open(path) as f:
            database = json.load(f)
    except FileNotFoundError:
        database = {}
    return database


def save_database(database:dict[str, dict], path:str) -> None:
    with open(path,"w") as f:
        json.dump(database, f)


def get_supported_queries() -> dict[str, dict]:
    return {
        "add": {"target": add_task,
                "help": "Adds a task into the lists of tasks",
                "args": [
                    {
                        "name_or_flags":["description"],
                        "help": "Description of the task"
                    }
                ]
                },
        "delete": {
            "target": delete_task,
            "help": "Delete a task from your task list",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "help": "ID of the task you want to delete",
                }
            ],
        },
        "update": {
            "target": update_task,
            "help": "Update the description of a task",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "help": "ID of the task to update",
                },
                {
                    "name_or_flags": ["description"],
                    "help": "New description for the task",
                },
            ],
        },
        "list": {
            "target": list_task,
            "help": "List all tasks or filter them by status",
            "args": [
                {
                    "name_or_flags": ["--status", "-s"],
                    "help": "Filter tasks by status (default is 'all')",
                    "choices": ["all", "done", "todo", "in-progress"],
                    "type": str.lower,
                    "default": "all",
                }
            ],
        },
        "mark-in-progress": {
            "target": mark_in_progress_task,
            "help": "Mark a task as 'in-progress'",
            "args": [{"name_or_flags": ["id"], "help": "ID of the task"}],
        },
        "mark-done": {
            "target": mark_done_task,
            "help": "Mark a task as 'done'",
            "args": [{"name_or_flags": ["id"], "help": "ID of the task"}],
        },
    }

def get_query(supported_queries: dict[str,dict]) -> tuple[Callable,dict]:
    parser: ArgumentParser = ArgumentParser(
        description="A CLI based task manager"
    )
    sub_parsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    for name, properties in supported_queries.items():
        p = sub_parsers.add_parser(name, help=properties["help"])
        for arg in properties["args"]:
            p.add_argument(*arg.pop("name_or_flags"), **arg)

    args:dict = parser.parse_args().__dict__
    query:Callable = supported_queries[args.pop("command")]["target"]

    return query,args


def add_task(database:dict[str,dict], description:str) -> None:
    today: str = datetime.today().isoformat();
    id: str = str(int(max("0",*database.keys()))+1)
    database[id] = {
        "description": description,
        "status": "todo",
        "created-at": today,
        "updated-at": today,
    }
    list_task({id: database[id]})


def delete_task(database:dict[str,dict], id:str) -> None:
    list_task({id: database[id]})
    del database[id]


def update_task(database:dict[str,dict], id:str, description:str) -> None:
    database[id]["description"] = description
    database[id]["updated-at"] = datetime.today().isoformat()
    list_task({id: database[id]})


def list_task(
        database:dict[str,dict],
        status:Literal["all","done","in-progress","todo"] = "all") \
        -> None:
    DATETIME_FORMAT: str = "%d/%m/%Y %H:%M:%S"

    table: Generator = (
        {
            "Id":id,
            "Description": properties["description"],
            "Status": properties["status"],
            "Created At": datetime.fromisoformat(properties["created-at"]).strftime(
                DATETIME_FORMAT
            ),
            "Updated At": datetime.fromisoformat(properties["updated-at"]).strftime(
                DATETIME_FORMAT
            ),
        }
        for id, properties in sorted(database.items(), key=lambda t: t[0])
        if status == "all" or status == properties["status"]
    )
    print(
        tabulate(table, tablefmt="rounded_grid", headers="keys") or "Nothing to display"
    )

def mark_in_progress_task(database:dict[str,dict], id:str) -> None:
    database[id]["status"] = "in-progress"
    database[id]["updated-at"] = datetime.today().isoformat()
    list_task({id: database[id]})

def mark_done_task(database:dict[str,dict], id:str) -> None:
    database[id]["status"] = "done"
    database[id]["updated-at"] = datetime.today().isoformat()
    list_task({id: database[id]})


if __name__ == "__main__":
    main()