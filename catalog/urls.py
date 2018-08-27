from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('books/', views.BookListView.as_view(), name='books'),
	path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
	path('authors/', views.AuthorListView.as_view(), name='authors'),
	path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
	#the name 'my-borrowed' is called by base-generic html in sidebar in a url link
	#<a href="{%url 'my-borrowed' %}">My Borrowed</a>
	#<li><a href="{% url 'my-borrowed' %}">My Borrowed</a></li>
	path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
	path('borrowedbooks/', views.LoanedBooksByLibrarianListView.as_view(), name='all-borrowed-books'),
	#path function has those params, 'path of relative url, the class or function in views.py, and the name of url
	#which is used in the html template file to hyperlink to it.
	path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
	path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),

	path('book/create/', views.BookCreate.as_view(), name='book_create'),
	path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
	path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),

]
