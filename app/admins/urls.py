from django.urls import path
from admins import views

app_name = 'admins'

urlpatterns = [
    path('create/', views.CreateAdminView.as_view(), name='create'),
    path('list/', views.ListUsersView.as_view(), name='list'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('promote/<int:pk>/', views.PromotingAdmin.as_view(), name='promote'),
    path('deactive/<int:pk>/', views.DeactiveAdmin.as_view(), name='deactive'),
    path('profile/<int:pk>/', views.AdminProfileAPIView.as_view(), name='profile'),
    path('me/picture/', views.ChangePictureAPIView.as_view(), name='profile-picture'),
    path('me/changepassword/', views.ChangePassword.as_view(), name='change-password')
]
