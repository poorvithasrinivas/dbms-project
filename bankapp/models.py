from django.db import models


class Account(models.Model):
    account_number = models.IntegerField(unique=True)
    customer_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    account_type = models.CharField(max_length=20)

    def __str__(self):
        return self.customer_name


class Transaction(models.Model):
    transaction_type = models.CharField(max_length=20)
    sender_account = models.IntegerField(null=True, blank=True)
    receiver_account = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.transaction_type