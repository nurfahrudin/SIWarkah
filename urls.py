from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from django.urls import path, re_path as url
from . import views

urlpatterns = [
    path('', views.index, name='index_warkah'),
    path('ajax/<params>/', views.ajax_combo, name='ajax_combo'),
    path('ajax_chart/', views.ajax_chart, name='ajax_chart'),
    path('ajax_dtbl/', views.ajax_table, name='ajax_table'),
    path('input/ajax/<params>/', views.ajax_combo, name='ajax_combo'),
    path('edit/<params_id>/ajax/<params>/', views.ajax_combo_edit, name='ajax_combo_edit'),

    path('input/', views.input, name='input_warkah'),
    path('edit/<int:id>/', views.edit, name='ubah_warkah'),
    path('delete/<int:id>/', views.delete, name='hapus_warkah'),

    path('accounts/login/', views.session_out, name='session_out'),
    path('media/<path>', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)