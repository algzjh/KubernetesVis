from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'k8svisapp1/index.html')
    # return HttpResponse("Hello World!")
    # return render("Hello World!")
