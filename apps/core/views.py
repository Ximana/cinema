from django.shortcuts import render, redirect

def home_view(request):
    #return render(request, 'core/home.html')
    return redirect('sessoes:lista')
