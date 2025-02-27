from .models import Listing, Realtor, ListingInstance, Genre
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import LoanListingForm
import datetime


def index(request):
    """View function for home page of site."""
    num_books = Listing.objects.all().count()
    num_instances = ListingInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = ListingInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Realtor.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_listings': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_realtors': num_authors,
        'num_visits': num_visits,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context=context)


class ListingListView(LoginRequiredMixin, generic.ListView):
    model = Listing


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Listing


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Realtor


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Realtor


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = ListingInstance
    template_name = 'catalog/my_books.html'
    paginate_by = 10

    def get_queryset(self):
        return ListingInstance.objects.filter \
            (borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AuthorCreate(CreateView):
    model = Listing
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('author_list'))


class AuthorUpdate(UpdateView):
    model = Realtor
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('realtor_list'))


def author_delete(request, pk):
    author = get_object_or_404(Realtor, pk=pk)
    try:
        author.delete()
        messages.success(request, (author.first_name + ' ' + author.last_name + " has been deleted"))
    except:
        messages.success(request, (
                    author.first_name + ' ' + author.last_name + ' cannot be deleted. Books exist for this author'))
    return redirect('author_list')


class AvailBooksListView(generic.ListView):
    """Generic class-based view listing all books on loan. """
    model = ListingInstance
    template_name = 'catalog/bookinstance_list_available.html'
    paginate_by = 10

    def get_queryset(self):
        return ListingInstance.objects.filter(status__exact='a').order_by('book__title')


def loan_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(ListingInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = LoanListingForm(request.POST, instance=book_instance)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (set due date and update status of book)
            book_instance = form.save()
            book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=4)
            book_instance.status = 'o'
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all_available'))
    # If this is a GET (or any other method) create the default form
    else:
        form = LoanListingForm(instance=book_instance, initial={'book_title': book_instance.book.title})

    return render(request, 'catalog/loan_book_librarian.html', {'form': form})

