from django.shortcuts import render

def privacy(request):
    return render(request, 'about/privacy.html')
def terms(request):
    return render(request, 'about/terms.html')
def about(request):
    return render(request, 'about/about.html' )