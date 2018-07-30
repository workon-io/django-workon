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
        return JsonResponse(self.get_json_data())

    def get_success_message_json_notice(self):
        return {
            'content': self.get_success_message(self.object),
            'classes': 'success'
        }

    def get_json_data(self):
        json = {
            'notice': self.get_success_message_json_notice()
        }
        messages.success(self.request, self.get_success_message(self.object))
        json['redirect'] = self.request.META['HTTP_REFERER']
        return json
        # return JsonResponse({
        #     'notice': {
        #         'content': f'{self.object} supprimé',
        #         'classes': 'success'
        #     },
        #     'remove': f'{self.object}_{self.object.pk}'
        # })



class ModalDelete(Delete):    
    template_name = "workon/views/delete/_modal.html"