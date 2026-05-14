from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from .forms import UserLoginForm
from django.conf.urls.static import static

urlpatterns = [
    path('', views.IndexView, name="home"),
    path('accounts/login/',LoginView.as_view(authentication_form=UserLoginForm, template_name='registration/login.html', redirect_authenticated_user=True),name="login_url"),
    path('register/',views.registerView,name="register_url"),
    path('logout/',LogoutView.as_view(next_page='home'),name="logout"),
    path('package/',views.PackageView,name="package"),
    path('flights/',views.FlightView,name="flights"),
    path('hotels/',views.HotelView,name="hotels"),
    path('places/',views.PlacesView,name="places"),
    path('bookflight/<str:flight_num>/<str:date>',views.Flightbook,name="bookflight"),
    path('userflight/<str:flight_num>/<str:date>/<int:seat>',views.FlightSubmit,name='userflight'),
    path('bookhotel/<str:hotel>/<str:date>',views.Hotelbook,name="bookhotel"),
    path('userhotel/<str:hotel>/<str:date>/<int:room>',views.HotelSubmit,name='userhotel'),
    path('bookpackage/<str:source>/<str:city>/<str:date>',views.PackageBook,name="bookpackage"),
    path('userpackage/<str:flight>/<str:hotel>/<str:date>/<int:room>/<int:seat>',views.PackageSubmit,name='userpackage'),
    path('accounts/profile/',views.Dashboard,name='dashboard'),
    path('cancelflight/<str:flight>/<str:date>/<int:seat>',views.CancelFlight,name='CancelFlight'),
    path('concanflight/<str:flight>/<str:date>/<int:seat>',views.ConfirmCancelFlight,name='ConfirmCancelFlight'),
    path('cancelhotel/<str:hotel>/<str:date>/<int:room>',views.CancelHotel,name='CancelHotel'),
    path('concanhotel/<str:hotel>/<str:date>/<int:room>',views.ConfirmCancelHotel,name='ConfirmCancelHotel'),
    path('cancelpackage/<str:flight>/<int:seat>/<str:hotel>/<str:date>/<int:room>',views.CancelPackage,name='CancelPackage'),
    path('concanpackage/<str:flight>/<int:seat>/<str:hotel>/<str:date>/<int:room>',views.ConfirmCancelPackage,name='ConfirmCancelPackage'),
    
    # NEW FEATURE URLS
    path('profile/', views.UserProfileView, name='profile'),
    path('flight-review/<int:flight_id>/', views.FlightReviewView, name='flight-reviews'),
    path('hotel-review/<int:hotel_id>/', views.HotelReviewView, name='hotel-reviews'),
    path('wishlist/add/<str:item_type>/<int:item_id>/', views.AddToWishlist, name='add-wishlist'),
    path('wishlist/', views.WishlistView, name='wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.RemoveFromWishlist, name='remove-wishlist'),
    path('discount/apply/', views.ApplyDiscountCode, name='apply-discount'),
    path('invoice/<str:booking_type>/<int:booking_id>/', views.GenerateInvoice, name='generate-invoice'),
    path('payment/<int:invoice_id>/', views.PaymentView, name='payment'),
    path('payment-success/<int:invoice_id>/', views.PaymentSuccessView, name='payment-success'),
    path('notifications/', views.NotificationsView, name='notifications'),
    path('notification/<int:notification_id>/mark-read/', views.MarkNotificationAsRead, name='mark-notification-read'),
    path('search-history/', views.SearchHistoryView, name='search-history'),
    path('api/autocomplete/', views.AutocompleteAPI, name='api-autocomplete'),
    path('api/notifications/unread-count/', views.UnreadNotificationCountAPI, name='api-unread-notifications'),
    path('booking-history/', views.BookingHistoryView, name='booking-history'),
    path('loyalty-points/', views.LoyaltyPointsView, name='loyalty-points'),
    path('add-hotel/', views.AddHotelView, name='add_hotel'),
    ]

urlpatterns+= staticfiles_urlpatterns()
urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
