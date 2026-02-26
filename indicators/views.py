from django.shortcuts import render, redirect, get_object_or_404
from .models import Indicator
from .forms import IndicatorForm
from django.contrib.auth.decorators import login_required


@login_required
def indicators_dashboard(request):
    indicators = Indicator.objects.all()

    # Handle add form directly on dashboard
    if request.method == "POST":
        form = IndicatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("indicators_dashboard")
    else:
        form = IndicatorForm()

    return render(request, "indicators/dashboard.html", {"indicators": indicators, "form": form})

@login_required
def edit_indicator(request, pk):
    indicator = get_object_or_404(Indicator, pk=pk)
    if request.method == "POST":
        form = IndicatorForm(request.POST, request.FILES, instance=indicator)
        if form.is_valid():
            form.save()
            return redirect("indicators_dashboard")
    else:
        form = IndicatorForm(instance=indicator)
    return render(request, "indicators/edit_indicator.html", {"form": form, "indicator": indicator})

@login_required
def delete_indicator(request, pk):
    indicator = get_object_or_404(Indicator, pk=pk)
    if request.method == "POST":
        indicator.delete()
        return redirect("indicators_dashboard")
    return render(request, "indicators/delete_indicator.html", {"indicator": indicator})

####################################################################################################
