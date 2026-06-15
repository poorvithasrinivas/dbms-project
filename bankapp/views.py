from django.shortcuts import render, redirect
from django.db.models import Sum   # Import Sum for aggregate balance calculation
from .models import Account, Transaction
from decimal import Decimal


def dashboard(request):

    # --- Customer Search Logic ---
    # Read the search query from the GET parameter 'q'.
    # .strip() removes leading/trailing whitespace from the input.
    search_query = request.GET.get('q', '').strip()

    if search_query:
        # Filter accounts where:
        #   - customer_name contains the query (case-insensitive), OR
        #   - account_number exactly matches the query (if it is numeric).
        # icontains performs a case-insensitive substring match on the name.
        name_matches = Account.objects.filter(
            customer_name__icontains=search_query
        )

        # Only attempt an account-number lookup when the query is a digit string,
        # to avoid a ValueError from passing letters to an IntegerField filter.
        if search_query.isdigit():
            number_matches = Account.objects.filter(
                account_number=int(search_query)
            )
        else:
            number_matches = Account.objects.none()

        # Combine both querysets and remove any duplicate rows with distinct().
        accounts = (name_matches | number_matches).distinct()
    else:
        # No search query — return every account (default dashboard view).
        accounts = Account.objects.all()

    # --- Statistics for the summary cards ---
    # These always reflect the FULL database, not just the filtered results,
    # so the cards remain accurate regardless of any active search.

    # Count of all registered customers (accounts)
    total_customers = Account.objects.count()

    # Sum of all account balances; default to 0 if no accounts exist
    total_balance = Account.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0

    # Total number of transactions ever recorded
    total_transactions = Transaction.objects.count()

    return render(
        request,
        'dashboard.html',
        {
            'accounts': accounts,
            'total_customers': total_customers,
            'total_balance': total_balance,
            'total_transactions': total_transactions,
            # Pass the query back so the template can re-populate the search bar
            'search_query': search_query,
        }
    )


def add_customer(request):

    if request.method == "POST":

        Account.objects.create(
            account_number=request.POST['acc_no'],
            customer_name=request.POST['name'],
            balance=Decimal(request.POST['balance']),
            account_type=request.POST['type']
        )

        return redirect('/')

    return render(request,'add_customer.html')


def delete_customer(request,id):

    account=Account.objects.get(id=id)
    account.delete()

    return redirect('/')


def deposit(request):

    if request.method=="POST":

        acc_no=request.POST['account_number']

        amount=Decimal(request.POST['amount'])

        account=Account.objects.get(
            account_number=acc_no
        )

        account.balance += amount

        account.save()

        Transaction.objects.create(
            transaction_type="Deposit",
            receiver_account=acc_no,
            amount=amount
        )

        return redirect('/')

    return render(
        request,
        'deposit.html'
    )


def withdraw(request):

    if request.method=="POST":

        acc_no=request.POST['account_number']

        amount=Decimal(request.POST['amount'])

        account=Account.objects.get(
            account_number=acc_no
        )

        if account.balance>=amount:

            account.balance-=amount

            account.save()

            Transaction.objects.create(
                transaction_type="Withdraw",
                sender_account=acc_no,
                amount=amount
            )

        return redirect('/')

    return render(request,'withdraw.html')

def transfer(request):

    if request.method=="POST":

        sender_no=request.POST['sender']

        receiver_no=request.POST['receiver']

        amount=Decimal(request.POST['amount'])

        sender=Account.objects.get(
            account_number=sender_no
        )

        receiver=Account.objects.get(
            account_number=receiver_no
        )

        if sender.balance>=amount:

            sender.balance-=amount

            receiver.balance+=amount

            sender.save()

            receiver.save()

            Transaction.objects.create(
                transaction_type="Transfer",
                sender_account=sender_no,
                receiver_account=receiver_no,
                amount=amount
            )

        return redirect('/')

    return render(request,'transfer.html')

def transactions(request):

    data=Transaction.objects.all().order_by('-id')

    return render(
        request,
        'transactions.html',
        {'data':data}
    )