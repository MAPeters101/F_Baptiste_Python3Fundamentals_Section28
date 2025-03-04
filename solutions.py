'''
Question 1
Write a custom class that will be used to model a single bank account.

Your class should implement functionality to:

allow initialization with values for first_name, last_name, account_number, balance, is_overdraft_allowed
keep track of a "ledger" that keeps a record all transactions (just use a list to keep track of this)
at a minimum it should keep track of the transaction date (the current UTC datetime) and the amount (positive, or negative to indicate deposits/withdrawals) - later you could add tracking the running balance as well.
provide read-only properties for first_name, last_name, account_number and balance
provide a property to access the ledger in such a way that a user of this class cannot mutate the ledger directly
provide a read-write property for is_overdraft_allowed that indicates whether overdrafts are allowed on the account.
provide methods to debit (def withdraw) and credit (def deposit) transactions that:
verify withdrawals against available balance and is_overdraft_allowed flag
if withdrawal is larger than available balance and overdrafts are not allowed, this should raise a custom OverdraftNotAllowed exception.
if transaction value is not positive, this should raise a ValueError exception (we have separate methods for deposits and withdrawals, and we expect the value to be positive in both cases - one will add to the balance, one will subtract from the balance).
add an entry to the ledger with a current UTC timestamp (positive or negative to indicate credit/debit)
keeps the available balance updated
implements a good string representation for the instance (maybe something like first_name last_name (account_number): balance
Feel free to expand on the minimum definition I have given here and enhance your custom class.

Solution
Let's start by writing the class and the __init__ method. We'll want to make the attributes first_name, last_name, account_number, balance read-only properties, so we'll use "private" variables for them at first, and then develop properties to access those values. We'll also create a property for is_overdraft_allowed - but we'll do that later.

class Account:
    def __init__(self, first_name, last_name, account_number, initial_balance):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
Now we should add read-only properties to our class for these attributes:

class Account:
    def __init__(self, first_name, last_name, account_number, initial_balance):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
Before we implement methods to record debits/credits, we'll want to have something we can use as a "ledger".

A simple way to implement this is to use a list internally, and expose that list via a property.

For simplicity, the values in the ledger will just be tuples containing the date and the amount (we could alternatively even construct custom classes for both the ledger and the ledger entries).

The issue is that lists are mutable, and we return the ledger from a property we'd like to make sure it cannot be mutated (and hence mutating our internal list).

There's two ways we could do this:

make a copy of the ledger and return that from the property
return a tuple of the internal ledger list
I'm just going to use the tuple approach, since whoever is using that class has no business modifying the ledger anyway, so that approach seems good enough.

class Account:
    def __init__(self, first_name, last_name, account_number, initial_balance):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
Next we need to implement is_overdraft_allowed.

We could just implememt this as a bare attribute, but I want to place some checks on when that value is set to ensure it is set to True or False only.

Let's start by writing the property getter and setter:

class Account:
    def __init__(self, first_name, last_name, account_number, initial_balance):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
Now we still have to initialize self._is_overdraft_allowed - we'll do that by allowing it in the class __init__ - however we also need to validate that it is a bool value there too - fortunately we can leverage our property setter.

While we're at it, we'll specify some suitable defaults for both the overdraft flag and the initial balance.

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed  # this uses the setter, and its validation logic

    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
Now we can go ahead an implement credits and debits.

For debits, we'll need to make sure that the available balance is sufficient to cover the debit if overdrafts are not allowed. If not, we'll want to raise a custom exception OverdraftNotAllowed.

Let's define that custom exception first:

class OverdraftNotAllowed(Exception):
    '''Exception indicating a transaction would have resulted in a forbidden overdraft.'''
Since both credits and debits will write the same thing to the same ledger (assuming the transaction goes through), we'll have some common code to add the entry to the ledger - so we'll write that as a "private" method we can use internally.

Let's implement that:

from datetime import datetime

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed  # this uses the setter, and its validation logic

    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value):
        dt = datetime.utcnow()
        self._ledger.append((dt, value))
Now let's go ahead and implement two methods for applying credits/debits to the account. If someone tries to create a non-positive valued transaction, we'll raise a ValueError.

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed  # this uses the setter, and its validation logic

    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value):
        dt = datetime.utcnow()
        self._ledger.append((dt, value))
        
    def deposit(self, value):
        # ensure value is positive
        if value <= 0:
            raise ValueError('Deposit value must be positive')
        
        # make entry in ledger
        self._make_ledger_entry(value)
        
        # and update balance
        self._balance += value
        
    def withdraw(self, value):
        # ensure value is positive
        if value <= 0:
            raise ValueError('Withdrawal value must be positive.')

        # can we make the withdrawal?
        if value > self.balance and not self.is_overdraft_allowed:
            # would result in overdraft, which is not allowed
            raise OverdraftNotAllowed(f'Would result in overdraft of {self.balance - value}')
            
        # ok to proceed
        # we'll just indicate withdrawals in ledger by using negative values
        self._make_ledger_entry(-value)
        # update balance
        self._balance -= value
There is another tweak I will want to make - adding the initial balance to the ledger - as well as keeping track of a running balance in the ledger itself - so I'm going to modify the __init__ method to add that ledger entry, as well as modify the _make_ledger_entry method to receive and store the current balance. Of course, I'll have to modify the withdraw and deposit methods to account for this new argument in _make_ledger_entry.

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed  # this uses the setter, and its validation logic
        self._make_ledger_entry(0, initial_balance)
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value, current_balance):
        dt = datetime.utcnow()
        self._ledger.append((dt, value, current_balance))
        
    def deposit(self, value):
        if value <= 0:
            raise ValueError('Deposit value must be positive')
        self._balance += value
        self._make_ledger_entry(value, self.balance)
        
    def withdraw(self, value):
        if value <= 0:
            raise ValueError('Withdrawal value must be positive.')
        if value > self.balance and not self.is_overdraft_allowed:
            raise OverdraftNotAllowed(f'Would result in overdraft of {self.balance - value}')
        self._balance -= value
        self._make_ledger_entry(-value, self.balance)
Finally, we should add some special methods for __str__ and __repr__.

(I'm also going to clean up comments that do not really add to the class, since most of the comments are rather obvious from the code itself).

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed
        self._make_ledger_entry(0, initial_balance)
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value, current_balance):
        dt = datetime.utcnow()
        self._ledger.append((dt, value, current_balance))
        
    def deposit(self, value):
        if value <= 0:
            raise ValueError('Deposit value must be positive')
        self._balance += value
        self._make_ledger_entry(value, self.balance)
        
    def withdraw(self, value):
        if value <= 0:
            raise ValueError('Withdrawal value must be positive.')
        if value > self.balance and not self.is_overdraft_allowed:
            raise OverdraftNotAllowed(f'Would result in overdraft of {self.balance - value}')
        self._balance -= value
        self._make_ledger_entry(-value, self.balance)
        
    def __repr__(self):
        return (
            f'({self.account_number}) {self.last_name}, '
            f'balance: {self.balance}, '
            f'overdraft: {self.is_overdraft_allowed}, '
            f'# transaction: {len(self._ledger)}'
        )
    
    def __str__(self):
        return f'{self.account_number}: {self.balance}'
Ok, that's pretty much my implementation at this point.

Let's try this class out and see how it works.

Note: I'm only going to test a few scenarios - this is by far not enough to fully test my code. In practice you should write a lot of tests to ensure your code works not only for the "standard" way things are expected to work (sometimes called "happy path"), but also tests that it handles "edge" (out of the ordinary and weird) conditions too.

acct = Account('John', 'Smith', '123456', 0)
By default, the overdraft flag should be False - we can use the assert statement to test this.

acct.is_overdraft_allowed
False
The ledger should be a tuple with a single entry for the initial balance at this point:

acct.ledger
((datetime.datetime(2021, 2, 7, 17, 58, 27, 130634), 0, 0),)
Let's try to make a withdrawal - that shoudl raise an OverdraftNotAllowed exception:

try:
    acct.withdraw(10)
except OverdraftNotAllowed as ex:
    print('OverdraftNotAllowed', ex)
OverdraftNotAllowed Would result in overdraft of -10
Now let's change the overdraft flag and try this again:

acct.is_overdraft_allowed = True
acct.withdraw(10)
No exception, that's good - and let's check the ledger:

acct.ledger
((datetime.datetime(2021, 2, 7, 17, 58, 27, 130634), 0, 0),
 (datetime.datetime(2021, 2, 7, 17, 58, 27, 151348), -10, -10))
Now let's try to make a negative transaction, we expect a ValueError on both deposit and withdraw:

try:
    acct.deposit(0)
except ValueError as ex:
    print(ex)
    
try:
    acct.deposit(-1)
except ValueError as ex:
    print(ex)
Deposit value must be positive
Deposit value must be positive
try:
    acct.withdraw(0)
except ValueError as ex:
    print(ex)
    
try:
    acct.withdraw(-1)
except ValueError as ex:
    print(ex)
Withdrawal value must be positive.
Withdrawal value must be positive.
Let's also see how our __repr__ works:

acct
(123456) Smith, balance: -10, overdraft: True, # transaction: 2
And our __str__:

print(acct)
123456: -10
Question 2
Expand on your class above to implement equality (==) comparisons between instances of your class.

Two accounts should be considered equal if the account numbers are the same.

Solution
We need to implement the __eq__ method and just make sure that:

both objects being compared are Account instances
check if the account_number value is the same.
class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed
        self._make_ledger_entry(0, initial_balance)
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value, current_balance):
        dt = datetime.utcnow()
        self._ledger.append((dt, value, current_balance))
        
    def deposit(self, value):
        if value <= 0:
            raise ValueError('Deposit value must be positive')
        self._balance += value
        self._make_ledger_entry(value, self.balance)
        
    def withdraw(self, value):
        if value <= 0:
            raise ValueError('Withdrawal value must be positive.')
        if value > self.balance and not self.is_overdraft_allowed:
            raise OverdraftNotAllowed(f'Would result in overdraft of {self.balance - value}')
        self._balance -= value
        self._make_ledger_entry(-value, self.balance)
        
    def __repr__(self):
        return (
            f'({self.account_number}) {self.last_name}, '
            f'balance: {self.balance}, '
            f'overdraft: {self.is_overdraft_allowed}, '
            f'# transaction: {len(self._ledger)}'
        )
    
    def __str__(self):
        return f'{self.account_number}: {self.balance}'
    
    def __eq__(self, other):
        if isinstance(other, Account) and self.account_number == other.account_number:
            return True
        return False
This code works fine, but whenever you see code that return True or return False based on evaluating a conditional expression, you really ought to re-write it to just return the result of the conditional expression.

class Account:
    def __init__(
        self, 
        first_name, 
        last_name, 
        account_number, 
        initial_balance = 0, 
        is_overdraft_allowed = False
    ):
        self._first_name = first_name
        self._last_name = last_name
        self._account_number = account_number
        self._balance = initial_balance
        self._ledger = []
        self.is_overdraft_allowed = is_overdraft_allowed
        self._make_ledger_entry(0, initial_balance)
        
    @property
    def first_name(self):
        return self._first_name
    
    @property
    def last_name(self):
        return self._last_name
    
    @property
    def account_number(self):
        return self._account_number
    
    @property
    def balance(self):
        return self._balance
    
    @property
    def ledger(self):
        return tuple(self._ledger)
    
    @property
    def is_overdraft_allowed(self):
        return self._is_overdraft_allowed
    
    @is_overdraft_allowed.setter
    def is_overdraft_allowed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Must be a bool.')
        self._is_overdraft_allowed = value
    
    def _make_ledger_entry(self, value, current_balance):
        dt = datetime.utcnow()
        self._ledger.append((dt, value, current_balance))
        
    def deposit(self, value):
        if value <= 0:
            raise ValueError('Deposit value must be positive')
        self._balance += value
        self._make_ledger_entry(value, self.balance)
        
    def withdraw(self, value):
        if value <= 0:
            raise ValueError('Withdrawal value must be positive.')
        if value > self.balance and not self.is_overdraft_allowed:
            raise OverdraftNotAllowed(f'Would result in overdraft of {self.balance - value}')
        self._balance -= value
        self._make_ledger_entry(-value, self.balance)
        
    def __repr__(self):
        return (
            f'({self.account_number}) {self.last_name}, '
            f'balance: {self.balance}, '
            f'overdraft: {self.is_overdraft_allowed}, '
            f'# transaction: {len(self._ledger)}'
        )
    
    def __str__(self):
        return f'{self.account_number}: {self.balance}'
    
    def __eq__(self, other):
        return isinstance(other, Account) and self.account_number == other.account_number
Let's test this out and see if it works as expected:

a1 = Account('f1', 'l1', '123')
a2 = Account('f2', 'l2', '123')

a1 == a2
True
a1 = Account('f1', 'l1', '123')
a2 = Account('f2', 'l2', '1234')

a1 == a2
False
As you can see equality is based solely on the account number and seems to work properly.
'''