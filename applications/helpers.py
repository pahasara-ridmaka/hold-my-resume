from django.shortcuts import render


def render_htmx(request, partial_template, full_template='applications/index.html', context=None):
    if context is None:
        context = {}

    if request.headers.get('HX-Request'):
        return render(request, partial_template, context)

    context['content_template'] = partial_template
    return render(request, full_template, context)