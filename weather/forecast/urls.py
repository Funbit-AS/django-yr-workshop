from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.location, name="location"),
    path("new-location/", views.CreateLocationView.as_view(), name="new-location"),
]
