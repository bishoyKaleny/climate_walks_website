from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    #path('',views.api_home),
    path('home/',views.home),
    path('',views.landing_page),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('tables/',views.read_tables,name='tables'),
    path('show_table/<str:pk>/',views.show_table),
    path('show_map/<str:pk>/',views.run_map),
    path('display_csv/<str:pk>/',views.display_csv),
    path('show_tables_by_day/<str:pk>/',views.days_tables),
    path('delete/<str:pk>/',views.delete_table),
    path('get_processed_data/<str:pk>/',views.get_processed_data)
]
urlpatterns += staticfiles_urlpatterns()
