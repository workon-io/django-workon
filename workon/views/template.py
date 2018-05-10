from django.views import generic


__all__ = ['Template']


class Template(generic.TemplateView):
    
    def get_template_names(self):
        if self.request.is_ajax():
            return getattr(self, 'ajax_template_name', 
                        getattr(self, 'template_name_ajax', 
                            getattr(self, 'xhr_template_name', 
                                getattr(self, 'template_name_xhr', 
                                    getattr(self, 'template_name')
                                )
                            )

                        )
                    )
        else:
            return self.template_name
