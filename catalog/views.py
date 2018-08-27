from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import  get_object_or_404
from django.http import HttpResponseRedirect
import datetime
from django.urls import reverse

from catalog.forms import RenewBookForm, RenewBookModelForm
from django.contrib.auth.decorators import permission_required

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy as _

class BookListView(generic.ListView):
	model = Book
	#context_object_name = 'books_list'  # your own name for the list as a template variable

	def get_queryset(self):
		return Book.objects.filter(title__icontains='the')[:5]  # Get 5 books containing the title war

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get the context
		context = super(BookListView, self).get_context_data(**kwargs)
		# Create any data and add it to the context
		context['some data'] = 'This is just some data'
		return context


class BookDetailView(generic.DetailView):
	model = Book


class AuthorListView(generic.ListView):
	model = Author
	#context_object_name = 'books_list'  # your own name for the list as a template variable

	def get_queryset(self):
		#return Author.objects.filter(first_name__icontains='a')[:5]  # Get 5 authors containing the title war
		return Author.objects.all()  #(first_name__icontains='a')[:5]  # Get 5 authors containing the title war

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get the context
		context = super(AuthorListView, self).get_context_data(**kwargs)
		# Create any data and add it to the context
		context['is_paginated'] = True
		return context


class AuthorDetailView(generic.DetailView):
	model = Author

	#render generates html files using a template and data
	# Create your views here.

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by =  10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).\
			filter(status__exact='o').order_by('due_back')


class LoanedBooksByLibrarianListView(PermissionRequiredMixin, generic.ListView):
	permission_required = 'catalog.can_mark_returned'
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_lib.html'
	paginate_by =  10

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


def index(request):
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	num_instance_available = BookInstance.objects.filter(status__exact='a').count()
	num_book_line = Book.objects.filter(title__icontains='line').count()

	num_authors = Author.objects.count()
	num_genres = Genre.objects.count()
	# Number of visits to this view, as counted in the session variable.
	#num_visits = request.session.get('num_visits', 0)
	num_of_visits= request.session.get('num_of_visits',0)

	#request.session['num_visits'] = num_visits + 1
	request.session['num_of_visits'] = num_of_visits + 1

	context = {
		'num_books':num_books,
		'num_instances':num_instances,
		'num_instance_available':num_instance_available,
		'num_authors':num_authors,
		'num_genres':num_genres,
		'num_book_line':num_book_line,
		#'num_visits': num_visits,
		'num_of_visits':num_of_visits,

	}
	#create and return an html page as a response
	return render(request, 'index.html', context=context)


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if book_renewal_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = book_renewal_form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed-books') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
	model = Author
	fields = '__all__'
	initial = {'date_of_death': '05/01/2018'}

	permission_required = 'catalog.can_mark_returned'
	success_url = _('authors')


class AuthorUpdate(UpdateView):
	model = Author

	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
	model = Author
	success_url = _('authors')


class BookCreate(CreateView):
	model = Book
	fields = '__all__'
	initial = {'language':'English'}
	success_url = _('books')


class BookUpdate(UpdateView):
	model = Book

	fields = ['title', 'author', 'summary', 'isbn']


class BookDelete(DeleteView):
	model=Book
	success_url = _('books')
