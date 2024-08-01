from django.urls import path
from .views import GenerateShortenedURLView, RedirectView, AnalyticsView, UpdateShortenedURLView, DeleteShortenedURLView

urlpatterns = [
    path('shorten/', GenerateShortenedURLView.as_view(), name='generate'),
    path('<str:alias>/', RedirectView.as_view(), name='redirect'),
    path('analytics/<str:alias>/', AnalyticsView.as_view(), name='analytics'),
    path('update/<str:alias>/', UpdateShortenedURLView.as_view(), name='update'),
    path('delete/<str:alias>/', DeleteShortenedURLView.as_view(), name='delete'),
]
