# ventas/urls.py
"""URLs de la app ventas — W09."""
from django.urls import path

from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='lista'),
    # Alias 'inicio': base.html y bienvenida (W02) usan '<app>:inicio'
    path('', views.VentaListView.as_view(), name='inicio'),
    path('<int:venta_id>/', views.VentaDetailView.as_view(), name='detalle'),
    # Escritura (W08)
    path('nueva/', views.crear_venta, name='crear'),
    path('<int:venta_id>/eliminar/', views.VentaDeleteView.as_view(), name='eliminar'),
]
