# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from random import randint
from datetime import datetime, timedelta

from amundsen_application.models.announcements import Announcements, Post
from amundsen_application.base.base_announcement_client import BaseAnnouncementClient

try:
    from sqlalchemy import Column, Integer, String, DateTime, create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
except ModuleNotFoundError:
    pass

Base = declarative_base()


class DBAnnouncement(Base):  # type: ignore
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True)

    date = Column(DateTime)
    title = Column(String)
    content = Column(String)


class SQLAlchemyAnnouncementClient(BaseAnnouncementClient):
    def __init__(self) -> None:
        self._setup_mysql()

    def _setup_mysql(self) -> None:
        self.engine = create_engine('sqlite:////tmp/amundsen.db', echo=True)

        session = sessionmaker(bind=self.engine)()

        # add dummy announcements to preview
        if not self.engine.dialect.has_table(self.engine, DBAnnouncement.__tablename__):
            Base.metadata.create_all(self.engine)

            announcements = []

            session.add_all(announcements)
            session.commit()

    def get_posts(self) -> Announcements:
        """
        Returns an instance of amundsen_application.models.announcements.Announcements, which should match
        amundsen_application.models.announcements.AnnouncementsSchema
        """
        session = sessionmaker(bind=self.engine)()

        posts = []

        for row in session.query(DBAnnouncement).order_by(DBAnnouncement.date.desc()):
            post = Post(title=row.title,
                        date=row.date.strftime('%b %d %Y %H:%M:%S'),
                        html_content=row.content)
            posts.append(post)

        return Announcements(posts)
    
    def add_post(self, title: str, content: str) -> None:
        """Add a new announcement post to the database."""
        session = sessionmaker(bind=self.engine)()
        try:
            new_announcement = DBAnnouncement(
                date=datetime.now(),
                title=title,
                content=content
            )
            session.add(new_announcement)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
