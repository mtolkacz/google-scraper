class ResultsMixin(object):
    @staticmethod
    def get_result(request):
        if 'result' in request.session:
            result = request.session['result']
            del request.session['result']
            return result
