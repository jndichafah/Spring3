from .models import ListingInstance
from django import forms


class LoanListingForm(forms.ModelForm):
    """Form for a librarian to loan books."""
    # Disable the book field to prevent user from entering a book
    # book_title is for display purposes only - set required=False
    book_title = forms.CharField(disabled=True, required=False)

    class Meta:
        # display only the book title and the borrower to the librarian
        model = ListingInstance
        fields = ('book_title', 'borrower',)
