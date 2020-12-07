from django.urls import path
from .views import ResultsView, ScraperView

app_name = "google_scraper.scraper"

urlpatterns = [
    path(
        route='',
        view=ScraperView.as_view(),
        name='index',
    ),
    path(
        route='results/',
        view=ResultsView.as_view(),
        name='results',
    ),
]

