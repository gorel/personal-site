"""
Adapted from
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
"""

import flask

from personal_site import constants, db


def add_to_index(index, model):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    flask.current_app.elasticsearch.index(
        index=index,
        doc_type=index,
        id=model.id,
        body=payload,
    )

def remove_from_index(index, model):
    flask.current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)

def query_index(index, query, page=1, per_page=constants.ES_PAGE_SIZE):
    results = flask.current_app.elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            "query": {"multi_match": {"query": query, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )
    ids = [int(res["_id"]) for res in results["hits"]["hits"]]
    return ids, results["hits"]["total"]


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page=1, per_page=constants.ES_PAGE_SIZE):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        else:
            when = [(ids[i], i) for i in range(len(ids))]
            return cls.query.filter(
                cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


# Register db event listeners
db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)
