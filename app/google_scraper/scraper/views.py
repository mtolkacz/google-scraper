from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from .forms import QueryForm
from .mixins import ResultsMixin


class ScraperView(View):
    """
    A homepage of Google scraper

    GET: Render query form. User can write query in the form's field.
    POST: Set session variable "query" with form data and redirect to results CBV.
    """

    form_class = QueryForm
    template_name = 'scraper/index.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            request.session['result'] = query
            return redirect(reverse('scraper:results'))

        return render(request, self.template_name, {'form': form})


class ResultsView(ResultsMixin, View):
    """
    Results View
    """

    template_name = 'scraper/results.html'

    def get(self, request, *args, **kwargs):

        result = self.get_result(request)

        return render(request, self.template_name, {'results': result}) if result else redirect('scraper:index')

