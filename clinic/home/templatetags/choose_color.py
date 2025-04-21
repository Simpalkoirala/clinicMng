from django import template

register = template.Library()

@register.simple_tag
def get_doc_type_color(doc_type, which):
        """
        Returns the Tailwind class associated with a given document type.
        `which` can be:
        - 'both' => returns "bg-xxx text-xxx"
        - 'bg'   => returns "bg-xxx"
        - 'text' => returns "text-xxx"
        
        Usage: {% get_doc_type_color doc.doc_type 'both' %}
        """

        class_map = {
            "PRESCRIPTION": {
                "bg": "bg-yellow-100",
                "text": "text-yellow-800"
            },
            "LAB_REPORT": {
                "bg": "bg-purple-100",
                "text": "text-purple-800"
            },
            "X_RAY": {
                "bg": "bg-green-100",
                "text": "text-green-800"
            },
            "OTHER_REPORT": {
                "bg": "bg-orange-100",
                "text": "text-orange-800"
            },
            "BLOOD_REPORT": {
                "bg": "bg-red-100",
                "text": "text-red-800"
            },
            "MRI": {
                "bg": "bg-blue-100",
                "text": "text-blue-800"
            }
        }

        default_class = {
            "bg": "bg-gray-100",
            "text": "text-gray-800"
        }

        classes = class_map.get(doc_type, default_class)

        if which == "bg":
            return classes["bg"]
        elif which == "text":
            return classes["text"]
        elif which == "both":
            return f"{classes['bg']} {classes['text']}"
        else:
            return ""