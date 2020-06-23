# from django.contrib.auth.models import User
# from django.test.client import Client
#
# # store the password to login later
# password = 'mypassword'
#
# my_admin = User.objects.create_superuser('myuser', 'myemail@test.com', password)
#
# c = Client()
#
# # You'll need to log him in before you can send requests through the client
# c.login(username=my_admin.username, password=password)