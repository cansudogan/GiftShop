from django.template import Template , Context
from django.shortcuts import render, render_to_response
from django.views import View
from django.db import connection
from django.conf import settings
from .forms import UserLoginForm, UserEditForm, UserRegistrationForm, ReportForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.hashers import make_password
from datetime import datetime

'''
    with djangoda işim bitene kadar açık kal gibi anlamda
    db.close() yani bağlantıyı kapatmak için.
    with connection.cursor() as cursor:
        -> cursor benim için bu methodu çağırıyo.

    cursor.fetchone ve fetchall sqlden dönenleri almak için kullanılıyo.

    render -> requesti alıp bi template ile verdiğimiz objeleri renderlayarak response dönüyor.

    def get ve def post fonksiyonları class based viewda çalışan methodlar
    get -> sadece talepte bulunma (genel olarak)
    post -> sunucuya talepte bulunurken veride gönderme

    form.is_valid() -> güvenlik amaçlı kullanılıyor

'''


class KatalogDetay(View):

    def get(self, request, cat_id):
        self.cat_id = cat_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT itemID, name, price, image FROM item WHERE itemID in (SELECT itemID FROM item_category_has WHERE cID=%s)", [self.cat_id])
            gifts = cursor.fetchall()
            cursor.execute("SELECT cID, cName FROM category WHERE cID IN (SELECT DISTINCT cID FROM item_category_has)")
            catalogs = cursor.fetchall()
        return render( request, 'gifts.html', {'gifts': gifts, 'catalogs': catalogs, })


class ChooseGiftView(View):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT itemID, name, price, image FROM item")
            gifts = cursor.fetchall()
            cursor.execute("SELECT cID, cName FROM category WHERE cID IN (SELECT DISTINCT cID FROM item_category_has)")
            catalogs = cursor.fetchall()
        return render( request, 'gifts.html', {'gifts': gifts, 'catalogs': catalogs, })


class Hakkimizda(View):

    def get(self, request):
        form = ReportForm()
        return render(request, 'hakkimizda.html', {'form': form})

    def post(self, request):
        form = ReportForm(request.POST)
        if form.is_valid():
            userform = form.cleaned_data
            self.type = userform['type']
            self.content = userform['content']
            self.orderDate = datetime.utcnow()
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO report (rType, rDate, content) VALUES (%s, %s, %s)", [self.type, self.orderDate, self.content])
            return HttpResponseRedirect("/hakkimizda")
        else:
            messages.error(request, "Form hatalı")
            return HttpResponseRedirect('/hakkimizda')


class Login(View):

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            userform = form.cleaned_data
            user = authenticate(
                   username=userform['username'],
                   password=userform['password']
                   )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponseRedirect('/login')
            else:
                return HttpResponseRedirect('/login')

    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})


class Logout(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class Profile(View):

    def get(self, request):
        self.username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("SELECT username, first_name, last_name, email, address FROM auth_user WHERE username=%s", [self.username])
            user_obj = cursor.fetchone()

        return render(request, 'profil.html', {'user_obj': user_obj})


class ProfilDuzenle(View):

    def get(self, request):
        form = UserEditForm()

        return render(request, 'profil_duzenle.html', {'form': form})

    def post(self, request):
        self.params = []
        form = UserEditForm(request.POST)
        self.username = request.user.username

        if form.is_valid():
            self.userform = form.cleaned_data
            self.params.append(self.userform['first_name'])
            self.params.append(self.userform['last_name'])
            self.params.append(self.userform['email'])
            self.params.append(self.userform['address'])
            self.params.append(self.username)

            with connection.cursor() as cursor:
                cursor.execute("UPDATE auth_user SET first_name=%s, last_name=%s, email=%s, address=%s WHERE username=%s", self.params)

        return HttpResponseRedirect('/profil')


class HediyeDetay(View):

    def get(self, request, gift_id):
        self.gift_id = gift_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT itemID, name, price, image, size, content FROM item WHERE itemID=%s LIMIT 1", [self.gift_id])
            gift = cursor.fetchone()

        return render(request, 'gift.html', {'gift': gift})


class SepetDetay(View):

    def get(self, request):
        self.username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE username=%s", [self.username])
            self.userID = cursor.fetchone()
            cursor.execute("SELECT * FROM orderlist, orderlist_auth_user_monitor WHERE id=%s", [self.userID])
            self.order = cursor.fetchone()
            if self.order is None:
                return render( request, 'orders.html', {'orders': None, 'items': None })
            else:
                cursor.execute("SELECT * FROM item, orderlist_item_belongs WHERE orderlist_item_belongs.orderID=%s AND orderlist_item_belongs.itemID=item.itemID", [self.order[0]])
                self.items = cursor.fetchall()
                return render( request, 'orders.html', {'order': self.order, 'items': self.items })


class SepettenCikar(View):

    def get(self, request, item_id):
        self.username = request.user.username
        self.item_id = item_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE username=%s", [self.username])
            self.userid = cursor.fetchone()
            cursor.execute("SELECT orderID FROM orderlist_auth_user_monitor WHERE id=%s", [self.userid])
            self.orderid = cursor.fetchone()
            cursor.execute("SELECT price FROM item WHERE itemID=%s", [self.item_id])
            self.price = cursor.fetchone()
            cursor.execute("SELECT orderTotal FROM orderlist WHERE orderID=%s", [self.orderid])
            self.orderTotal = cursor.fetchone()
            cursor.execute("DELETE FROM orderlist_item_belongs WHERE orderID=%s AND itemID=%s",[self.orderid, self.item_id])
            self.orderTotal = int(self.orderTotal[0]) - int(self.price[0])
            if self.orderTotal is 0:
                cursor.execute("DELETE FROM orderlist_auth_user_monitor WHERE orderID=%s", [self.orderid])
                cursor.execute("DELETE FROM orderlist WHERE orderID=%s", [self.orderid])
            else:
                cursor.execute("UPDATE orderlist SET orderTotal=%s WHERE orderID=%s", [self.orderTotal, self.orderid])
        return HttpResponseRedirect('/sepetim')


class SepeteEkle(View):

    def get(self, request, gift_id):
        self.user = request.user
        if self.user.is_authenticated:
            self.username = request.user.username
            self.gift_id = gift_id
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM auth_user WHERE username=%s", [self.username])
                self.userID = cursor.fetchone()
                cursor.execute("SELECT orderID FROM orderlist_auth_user_monitor WHERE id=%s", [self.userID])
                self.orders = cursor.fetchone()
                if self.orders is None:
                    with connection.cursor() as cursor:
                        self.orderDate = datetime.utcnow()
                        cursor.execute("INSERT INTO orderlist (orderTotal, orderDate) VALUES (%s, %s)", ['0', self.orderDate])
                        cursor.execute("SELECT orderID FROM orderlist WHERE orderDate=%s", [self.orderDate])
                        self.orderid = cursor.fetchone()
                        cursor.execute("INSERT INTO orderlist_auth_user_monitor (orderID, id) VALUES (%s, %s)", [self.orderid, self.userID])
                        cursor.execute("INSERT INTO orderlist_item_belongs (orderID, itemID) VALUES (%s, %s)", [self.orderid, self.gift_id])
                        cursor.execute("SELECT item.price FROM item, orderlist_item_belongs WHERE item.itemID=orderlist_item_belongs.itemID")
                        self.itemPrice = cursor.fetchone()
                        cursor.execute("UPDATE orderlist SET orderTotal=%s WHERE orderID=%s", [self.itemPrice, self.orderid])

                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT orderID FROM orderlist_auth_user_monitor WHERE id=%s", [self.userID])
                        self.orderID = cursor.fetchone()
                        cursor.execute("INSERT INTO orderlist_item_belongs (orderID,itemID) VALUES (%s, %s)", [self.orderID, self.gift_id])
                        cursor.execute("SELECT price FROM item WHERE itemID=%s", [self.gift_id])
                        self.itemPrice = cursor.fetchone()
                        cursor.execute("SELECT orderTotal FROM orderlist WHERE orderID=%s", [self.orderID])
                        self.orderTotal = cursor.fetchone()
                        self.orderTotal= int(self.itemPrice[0]) + int(self.orderTotal[0])
                        cursor.execute("UPDATE orderlist SET orderTotal=%s WHERE orderID=%s", [self.orderTotal, self.orderID])
            return HttpResponseRedirect('/')

        else:

            return HttpResponseRedirect('/kayitol')


class FavoriDetay(View):

    def get(self, request):
        self.username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM item I WHERE I.itemID IN (SELECT F.itemID FROM favlist_has_item F WHERE F.fID IN (SELECT M.fID FROM member_create_favlist M WHERE M.id IN (SELECT id FROM auth_user WHERE username=%s)))", [self.username])
            self.items = cursor.fetchall()
            return render( request, 'favourites.html', {'favs': self.items})


class FavoriCikar(View):

    def get(self, request, item_id):
        self.username = request.user.username
        self.item_id = item_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM auth_user WHERE username=%s", [self.username])
            self.id = cursor.fetchone()
            cursor.execute("SELECT fID FROM member_create_favlist WHERE id=%s", [self.id])
            self.fID = cursor.fetchone()
            cursor.execute("DELETE FROM favlist_has_item WHERE fID=%s AND itemID=%s", [self.fID, self.item_id])

        return HttpResponseRedirect('/favorilerim')


class FavoriEkle(View):

    def get(self, request, gift_id):
        self.user = request.user
        self.gift_id = gift_id
        if self.user.is_authenticated:
            self.username = request.user.username
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM auth_user WHERE username=%s", [self.username])
                self.id = cursor.fetchone()
                cursor.execute("SELECT fID FROM member_create_favlist WHERE id=%s", [self.id])
                self.fID = cursor.fetchone()
                if self.fID is None:
                    cursor.execute("INSERT INTO member_create_favlist (id) VALUES (%s)", [self.id])
                    cursor.execute("SELECT fID FROM member_create_favlist WHERE id=%s", [self.fID])
                    self.fID = cursor.fetchone()
                cursor.execute("INSERT INTO favlist_has_item (fID, itemID) VALUES(%s, %s)", [self.fID, self.gift_id])
            return HttpResponseRedirect('/')
        else:
            messages.error(request, "Favori eklemek için kayıt olun")
            return HttpResponseRedirect('/kayitol')


class Registration(View):

    def post(self, request):
        self.params = ['0', '0', '1']
        self.now = datetime.now()
        self.params.append(self.now)
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            self.username = userObj['username']
            self.params.append(userObj['username'])
            self.password_unhashed = userObj['password']
            self.password = make_password(self.password_unhashed)
            #make_password djangonun hashleme methodu database passwordu plaintext olarak tutmamak için
            self.params.append(self.password)
            self.params.append(userObj['first_name'])
            self.params.append(userObj['last_name'])
            self.params.append(userObj['email'])
            self.params.append(userObj['address'])
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO auth_user (is_superuser, is_staff, is_active, date_joined, username, password, first_name, last_name, email, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", self.params)

            user = authenticate(username=self.username, password=self.password_unhashed)
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})


class Deletion(View):

    def get(self, request):
        self.username = request.user.username
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM auth_user WHERE username=%s", [self.username])
            logout(request)
        return HttpResponseRedirect('/')
