from django.conf.urls import url
from . import views

# viewsları import ettik çünkü url'e gelen requesti hangi viewa atcağımı burda belirliyoruz.


urlpatterns = [
    url(r'^$', views.ChooseGiftView.as_view()),
    url(r'hediyesec$', views.ChooseGiftView.as_view()),
    url(r'hakkimizda$', views.Hakkimizda.as_view()),
    url(r'login$', views.Login.as_view()),
    url(r'profil$', views.Profile.as_view()),
    url(r'kayitol$', views.Registration.as_view()),
    url(r'hesapsil$', views.Deletion.as_view()),
    url(r'profilduzenle$', views.ProfilDuzenle.as_view()),
    url(r'cikisyap$', views.Logout.as_view()),
    url(r'hediyeler/([0-9]+)$',views.HediyeDetay.as_view()),
    url(r'hediyeler/([0-9]+)/sepeteekle$',views.SepeteEkle.as_view()),
    url(r'sepettencikar/([0-9]+)$', views.SepettenCikar.as_view()),
    url(r'sepetim$', views.SepetDetay.as_view()),
    url(r'hediyeler/([0-9]+)/favoriekle$',views.FavoriEkle.as_view()),
    url(r'favoricikar/([0-9]+)$', views.FavoriCikar.as_view()),
    url(r'favorilerim$', views.FavoriDetay.as_view()),
    url(r'katalog/([0-9]+)$', views.KatalogDetay.as_view()),
]
