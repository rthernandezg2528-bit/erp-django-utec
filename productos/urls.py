# productos/urls.py
"""URLs de la app productos — W09."""
from django.urls import path

from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista'),
    # Alias 'inicio': base.html y bienvenida (W02) usan '<app>:inicio'
    path('', views.ProductoListView.as_view(), name='inicio'),
    path('<int:producto_id>/', views.ProductoDetailView.as_view(), name='detalle'),
    # Escritura (W08)
    path('nuevo/', views.ProductoCreateView.as_view(), name='crear'),
    path('<int:producto_id>/editar/', views.ProductoUpdateView.as_view(), name='editar'),
    path('<int:producto_id>/eliminar/', views.ProductoDeleteView.as_view(), name='eliminar'),
]
