from django import forms


__all__ = ['TreeSelect', 'TreeSelectMultiple', 'TreeModelChoiceField', 'TreeModelMultipleChoiceField']


class TreeModelChoiceIterator(forms.models.ModelChoiceIterator):

    def choice(self, obj):
        parent_id = getattr(obj, 'parent_id', None)
        level = getattr(obj, getattr(self.queryset.model._meta, 'level_attr', 'level'), 1)
        return super().choice(obj) + (parent_id, level, obj)

class TreeSelect(forms.SelectMultiple):

    template_name = "workon/forms/widgets/_treeselect.html"

    def __init__(self, *args, **kwargs):
        self.label_from_instance = kwargs.pop('label_from_instance', None)
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        by_ids = {}
        test_selected = lambda o: None
        if value:
            if isinstance(value, list):
                test_selected = lambda o: o in value
            else:
                test_selected = lambda o: o == value


        for choice in self.choices:
            if self.label_from_instance:
                label = self.label_from_instance(choice[4])
            else:
                label = choice[1]
            by_ids[choice[0]] = {
                'items': [],
                'is_selected': test_selected(choice[0]),
                'label': label,
                'parent_id': choice[2],
                'level': choice[3],
                'value': choice[0]
            }
        tree = {}
        for pk, item in by_ids.items():
            if item['parent_id']:
                by_ids[item['parent_id']]['items'].append(item)
                if item['is_selected']:
                    by_ids[item['parent_id']]['is_selected'] = True

            else:
                tree[pk] = item

        context = {
            'tree': tree.values(),
            'is_hidden': self.is_hidden,
            'name': name,
            'required': self.is_required,
            'value': self.format_value(value),
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
        }
        return context

class TreeSelectMultiple(TreeSelect, forms.SelectMultiple):

    template_name = "workon/forms/widgets/_treeselectmultiple.html"

class TreeModelChoiceField(forms.ModelMultipleChoiceField):
    widget = TreeSelect
    iterator = TreeModelChoiceIterator

class TreeModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = TreeSelectMultiple
    iterator = TreeModelChoiceIterator
