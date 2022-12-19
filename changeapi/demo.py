import datetime
from sqlalchemy.orm import Session
from sqlalchemy.engine import create_engine
from .data_model import ChangeList, ChangeListBranch, build_db, Build, DepotManifest

db_url = 'sqlite:///changeapi.db'
build_db(db_url)
engine = create_engine(db_url, echo=True, future=True)

with Session(engine) as session:
    for x in session.query(DepotManifest).all():
        print(f'{x.depot=}, {x.manifest=}')

    dms = [
        DepotManifest(depot=238961, manifest=8628579843003481755),
        DepotManifest(depot=238962, manifest=2542183516457273677),
        DepotManifest(depot=238963, manifest=141861304460106257),
    ]
    for dm in dms:
        session.merge(dm)

    time_changed = datetime.datetime.fromtimestamp(1654145723)
    cl = ChangeList(id=14997643, time_changed=time_changed)
    cl = session.merge(cl)

    time_updated = datetime.datetime.fromtimestamp(1654145721)
    clb = ChangeListBranch(name='public', time_updated=time_updated, build_id=8855727)
    clb.change_list = cl
    print(clb.change_list_id)
    clb = session.merge(clb)
    print(clb.change_list_id)    

    for x in session.query(DepotManifest).all():
        print(f'{x.depot=}, {x.manifest=}')

    session.commit()

    for cl in session.query(ChangeList).all():
        print(cl)