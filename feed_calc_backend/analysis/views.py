from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
def gap_analysis(request):  return JsonResponse({"gaps": []})
def cost_analysis(request): return JsonResponse({"cost": {}})
