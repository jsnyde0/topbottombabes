from urllib.parse import urlencode

def clean_filter_url(request):
    cleaned_params = {}
    for key, values in request.GET.lists():
        # Filter out empty values
        clean_values = [v for v in values if v]
        if clean_values:
            if len(clean_values) > 1:
                cleaned_params[key] = clean_values
            else:
                cleaned_params[key] = clean_values[0]
    
    if len(cleaned_params) < len(request.GET):
        base_url = request.path
        if cleaned_params:
            return f"{base_url}?{urlencode(cleaned_params, doseq=True)}"
        else:
            return base_url
    
    return None