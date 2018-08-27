import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, BookInstance, Book, Genre, Language
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import Permission

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors=12
        for id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Chris{id}',
                last_name=f'Kim{id}',
            )

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        #response.context, is the context variable passed to the template by the view
        #
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        #response = self.client.get(reverse('authors'))
        #response = self.client.get('/catalog/authors')
        response = self.client.get('/catalog/authors/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1234')
        test_user2 = User.objects.create_user(username='testuser2', password='1234')

        test_user1.save()
        test_user2.save()

        test_author = Author.objects.create(first_name='john', last_name='smith')
        test_genre = Genre.objects.create(name='Comics')
        test_language = Language.objects.create(name='Poland')

        test_book = Book.objects.create(
            title='Golen Era',
            summary='golen era, silver era, copper era',
            isbn='12344553233',
            author=test_author,
            language=test_language,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        number_of_copies = 30
        for book_copy in range(number_of_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'

            BookInstance.objects.create(
                book=test_book,
                imprint='unlikely imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,

            )

    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,'/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1234')
        response=self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')

        self.assertEqual(response.status_code,200)

        self.assertTemplateUsed(response,'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1234')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code,200)

        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)
        books = BookInstance.objects.all()[:10]

        for ibook in books:
            ibook.status = 'o'
            ibook.save()

        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username='testuser1',password='1234')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date=0

        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create(username='user1', password='1234')
        test_user2 = User.objects.create(username='user2', password='1234')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_user1.user_permissions.add(permission)
        test_user1.save()

        test_author = Author.objects.create(first_name='john',last_name='smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Silver Era',
            summary='silver era',
            isbn='1234556',
            author=test_author,
            #genre=test_genre,
            language=test_language,
        )

        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        return_day = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1= BookInstance.objects.create(
            book=test_book,
            imprint = 'imprint 1323',
            due_back=return_day,
            borrower=test_user2,
            status='o',
        )

        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='imprint 1343',
            due_back=return_day,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_loggin(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permsion(self):
        login = self.client.login(username='user1', password='1234')
        response=self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        self.client.login(username='user2', password='1234')

        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))


        print('wwwwwwwwwww', response.status_code)
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='user2', password='1234')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='user2', password='1234')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='user2', password='1234')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='user2', password='1234')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(days=4)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='user2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),\
                                    {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))