from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
def formula_pdf(request, pk: int):
    return HttpResponse(f"PDF for formula {pk}", content_type="text/plain")
