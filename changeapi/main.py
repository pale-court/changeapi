from pathlib import Path
from typing import Dict, Mapping, Optional

from fastapi import Body, FastAPI, HTTPException
from starlette import status
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import Session

from atomicwrites import atomic_write

import json

# from .data_model import build_db, ChangeList

# db_url = 'sqlite:///changeapi.db'
# build_db(db_url)
# engine = create_engine(db_url, echo=True, future=True)

app = FastAPI()


class Manifest(BaseModel):
    gid: str
    size: Optional[int] = None
    download: Optional[int] = None


class Build(BaseModel):
    build_id: int
    time_updated: Optional[str] = None
    version: Optional[str] = None
    manifests: Mapping[str, Manifest]


class MockChangeList(BaseModel):
    change_id: int
    branches: Mapping[str, Build]


class Settings(BaseSettings):
    state_dir: Path
    molly_guard: str


settings = Settings()

changes = {
    "14968957": {
        "change_id": 14968957,
        "branches": {
            "public": {
                "build_id": 8833106,
                "time_updated": "1653960565",
                "manifests": {
                    "238961": {
                        "gid": "1228835140409683710",
                    },
                    "238962": {
                        "gid": "6888634665108774252",
                    },
                    "238963": {
                        "gid": "8951794261227212849",
                    },
                },
            },
        },
    },
    "14997643": {
        "change_id": 14997643,
        "branches": {
            "public": {
                "build_id": 8855727,
                "time_updated": "1654145721",
                "manifests": {
                    "238961": {
                        "gid": "8628579843003481755",
                    },
                    "238962": {
                        "gid": "2542183516457273677",
                    },
                    "238963": {
                        "gid": "141861304460106257",
                    },
                },
            },
        },
    },
    "15128087": {
        "change_id": 15128087,
        "branches": {
            "public": {
                "build_id": 8930624,
                "time_updated": "1655251431",
                "manifests": {
                    "238961": {
                        "gid": "1751070635077352462",
                    },
                    "238962": {
                        "gid": "5654086130423198733",
                    },
                    "238963": {
                        "gid": "2996040912614990240",
                    },
                },
            },
        },
    },
}


settings.state_dir.mkdir(parents=True, exist_ok=True)
changes_path = settings.state_dir / "changes.json"
if changes_path.exists():
    with changes_path.open("r") as fh:
        changes = json.load(fh)

        # Convert the old change format that has manifest gids instead of dicts
        for cid, change in changes.items():
            for bid, branch in change["branches"].items():
                manifests = branch["manifests"]
                depot_ids = list(manifests.keys())
                for did in depot_ids:
                    mf = manifests[did]
                    if isinstance(mf, str):
                        manifests[did] = {"gid": mf}

# @app.get('/db-changelists')
# def read_db_changes():
#     with Session(engine) as session:
#         lists = session.query(ChangeList).all()
#         print(lists)


def save_changes():
    with atomic_write(changes_path, overwrite=True) as fh:
        json.dump(changes, fh, indent=4)


@app.get("/changelists")
def read_changes():
    return changes


@app.get("/changelists/{cl_id}")
def read_change(cl_id: int):
    return changes[str(cl_id)]


@app.put("/changelists/{cl_id}")
def write_change(cl: MockChangeList, molly_guard: str):
    if molly_guard != settings.molly_guard:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication"
        )
    cid = str(cl.change_id)
    if cid not in changes:
        changes[cid] = cl.model_dump()
        save_changes()
    else:
        old = MockChangeList(**changes[cid])
        for branch in old.branches:
            if branch in cl.branches and (v := old.branches[branch].version):
                if (b := cl.branches[branch]).version != v:
                    b.version = v
        changes[cid] = cl.model_dump()
        save_changes()


@app.get("/builds/{branch}")
def read_builds(branch: str):
    builds = {}
    for cid in sorted(changes.keys(), reverse=True):
        change = changes[cid]
        if branch in change["branches"]:
            b = change["branches"][branch]
            builds[b["build_id"]] = b

    return builds


@app.put("/builds/{branch}/{build_id}/version")
def write_version(branch: str, build_id: int, version: str, molly_guard: str):
    if molly_guard != settings.molly_guard:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication"
        )
    changed = False
    for cid in changes:
        change = changes[cid]
        if "branches" in change and branch in change["branches"]:
            bobj = change["branches"][branch]
            if bobj["build_id"] == build_id:
                bobj["version"] = version
                changed = True
    save_changes()
