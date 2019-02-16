from django.shortcuts import render
import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from cat_log.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from cat_log.models import Author
from cat_log.models import Book, BookInstance, Genre
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    fiction_books = Book.objects.filter(genre__name__icontains='Fiction').count()
    booktitle_with_th = Book.objects.filter(title__icontains='th').count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'fiction_books': fiction_books,
        'booktitle_with_th': booktitle_with_th,
        'num_authors': num_authors,
        'num_visits': num_visits,
        }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def author_index(request):
    book_by_author = Book.objects.filter(author__last_name__icontains='Rowan')
    context = {
        'author': book_by_author,
        }
    print(context)
    #return render(request, 'author_index.html', context=context)
    return render(request, 'cat_log/author_index.html', {'author': book_by_author})
from django.views import generic
#######################model_views####################################################
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10#pagenation
    #context_object_name = 'my_book_list'   # your own name for the list as a template variable
    #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    #template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location
    
class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
class AuthorDetailView(generic.DetailView):
    model = Author
    
from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='cat_log/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
class LoanedBooks_ByUserListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='cat_log/bookinstance_list_borrowed_to_users.html'
    paginate_by = 10
    permission_required = 'cat_log.can_mark_returned'
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
#######################BOOK_RENEWER####################################################
@permission_required('cat_log.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('br-books') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'cat_log/book_renew_librarian.html', context)

#######################UTHORS_BOOK####################################################
class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
#######################BOOK####################################################   
class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    initial = {'language': 'Yoruba'}

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    
