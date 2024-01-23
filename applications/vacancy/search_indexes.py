from haystack import indexes
from . import models


class ServiceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created = indexes.DateTimeField(model_attr='created')
    datetime = indexes.DateTimeField(model_attr='datetime')
    title_auto = indexes.EdgeNgramField(model_attr='title')
    body_auto = indexes.EdgeNgramField(model_attr='body')

    def get_model(self):
        return models.Vacancy

    def index_queryset(self, using=None):
        return self.get_model().published.all()
