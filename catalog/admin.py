from django.contrib import admin
from .models import Author, Genre, Book, Language, BookInstance

class BooksInstanceInline(admin.StackedInline):
	model = BookInstance
	extra = 1

#admin.site.register(Book)
@admin.register(Book)

class BookAdmin(admin.ModelAdmin):
	list_display = ('title','author','display_genre')
	inlines = [BooksInstanceInline]
	#pass


class BooksInline(admin.StackedInline):
	model = Book
	extra = 1

#admin.site.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ('last_name','first_name', 'date_of_birth','date_of_death')
	inlines = [BooksInline]

	#pass
admin.site.register(Author, AuthorAdmin)

admin.site.register(Genre)
admin.site.register(Language)
#admin.site.register(BookInstance)

@admin.register(BookInstance)

class BookInstanceAdmin(admin.ModelAdmin):
	list_display = ('status', 'due_back','id','display_book','borrower')

	list_filter = ('status', 'due_back')

	fieldsets = (
        	('Information', {
            		'fields': ('id', 'book', 'imprint')
        	}),
        	('Availability', {
            		'fields': ('status', 'due_back','borrower')
        	}),
    	)
	#pass

# Register your models here.
