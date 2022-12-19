from pkg_resources import declare_namespace
from sqlalchemy import BigInteger, Column, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class ChangeList(Base):
    __tablename__ = 'change_list'
    id = Column(Integer, primary_key=True)
    time_changed = Column(TIMESTAMP)


class Build(Base):
    __tablename__ = 'build'
    id = Column(Integer, primary_key=True)
    # build_depots = relationship('BuildDepot', backref='build_id')


class DepotManifest(Base):
    __tablename__ = 'depot_manifest'
    depot = Column(Integer, primary_key=True)
    manifest = Column(BigInteger, primary_key=True)
    builds = relationship('BuildDepot', backref='depot_manifest')


class BuildDepot(Base):
    __tablename__ = 'build_depot'
    build_id = Column(Integer, ForeignKey('build.id'), primary_key=True)
    depot_manifest_depot = Column(Integer, primary_key=True)
    depot_manifest_manifest = Column(BigInteger, primary_key=True)
    __table_args__ = (ForeignKeyConstraint([depot_manifest_depot, depot_manifest_manifest], [
                      DepotManifest.depot, DepotManifest.manifest]), {})


class ChangeListBranch(Base):
    __tablename__ = 'change_list_branch'
    change_list_id = Column(Integer, ForeignKey('change_list.id'), primary_key=True)
    name = Column(String, primary_key=True)
    build_id = Column(Integer, ForeignKey('build.id'))
    time_updated = Column(BigInteger)
    change_list = relationship(ChangeList)
    build = relationship(Build)


def build_db(path):
    engine = create_engine(path)
    Base.metadata.create_all(engine)
    return engine
