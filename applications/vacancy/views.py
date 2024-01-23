from haystack.query import SearchQuerySet, SQ
from haystack.generic_views import SearchView
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django.http import JsonResponse

from .models import Vacancy, Company


def vacancy_list(request):
    vacancies = Vacancy.published.all().order_by('-datetime')
    return render(request, 'vacancy/vacancy/list.html', {'vacancies': vacancies, 'vacancies_count': len(vacancies)})


def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    vacancy_dict = model_to_dict(vacancy)
    stop_field = ['id', 'title', 'body', 'date', 'slug', 'status', 'company', 'vacancy_id']
    return render(
        request,
        'vacancy/vacancy/detail.html',
        {'vacancy': vacancy, 'vacancy_dict': vacancy_dict, 'stop_field': stop_field},
    )


def company_list(request):
    companies = Company.objects.all()
    return render(request, 'vacancy/company/list.html', {'companies': companies, 'companies_count': len(companies)})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company_dict = model_to_dict(company)
    stop_field = ['name', 'created', 'photos']
    return render(
        request,
        'vacancy/company/detail.html',
        {'company': company, 'company_dict': company_dict, 'stop_field': stop_field},
    )


def autocomplete(request):
    results = []
    max_items = 50
    q = request.GET.get('q')
    if q:
        title_sqs = SearchQuerySet().autocomplete(title_auto=q).order_by('-datetime')
        body_sqs = SearchQuerySet().autocomplete(body_auto=q).order_by('-datetime')
        sqs = title_sqs | body_sqs
        results = [[result.object.title, str(result.object.pk)] for result in sqs[:max_items]]
    return JsonResponse({'results': results})


class VacancySearchView(SearchView):

    def get_search_result(self):
        qs = self.get_queryset()
        q = None
        day = None
        sort_by = None
        results = []

        if self.request.method == "GET":
            q = self.request.GET.get('q', '')
            day = self.request.GET.get('start_day', '')
            sort_by = self.request.GET.get('sort_by', '')

        if q:
            if day and day.isdigit():
                start_date = date.today() - timedelta(days=int(day))
                title_results = qs.autocomplete(title_auto=q).filter(created__gte=start_date)
                body_results = qs.autocomplete(body_auto=q).filter(created__gte=start_date)
            else:
                title_results = qs.autocomplete(title_auto=q)
                body_results = qs.autocomplete(body_auto=q)

            results = title_results | body_results

        if results:
            if sort_by == 'new':
                results = results.order_by('-datetime')
            elif sort_by == 'old':
                results = results.order_by('datetime')

        return results

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'results_count': len(context['object_list'])})
        return context

    def form_valid(self, form):
        self.queryset = self.get_search_result()
        context = self.get_context_data(
            **{
                self.form_name: form,
                "query": form.cleaned_data.get(self.search_field),
                "object_list": self.queryset,
            }
        )
        return self.render_to_response(context)
