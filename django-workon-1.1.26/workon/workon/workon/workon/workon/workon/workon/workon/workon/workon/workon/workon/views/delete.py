from django.views import generic
from django.http import JsonResponse
from django.contrib import messages


__all__ = ['Delete', 'ModalDelete']


class Delete(generic.DeleteView):

    def get_success_message(self, obj):
        return f'{obj} supprimé'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = self.object.pk
        self.object.delete()

        success_message = self.get_success_message(self.object)
        json = {
            'notice': {
                'content': success_message,
                'classes': 'success'
            },
        }

        messages.success(self.request, success_message)
        json['redirect'] = self.request.META['HTTP_REFERER']

        # return JsonResponse({
        #     'notice': {
        #         'content': f'{self.object} supprimé',
        #         'classes': 'success'
        #     },
        #     'remove': f'{self.object}_{self.object.pk}'
        # })

        return JsonResponse(json)


class ModalDelete(Delete):    
    template_name = "workon/views/delete/_modal.html"