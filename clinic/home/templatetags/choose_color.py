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
        


@register.simple_tag
def get_status_type_color(status_type):
    """
    Returns the Tailwind class associated with a given appoinment status type.
    Usage: {% get_status_type_color appoinment.status %}
    """
    class_map = {
        "pending": "bg-orange-50 text-orange-700 border-orange-100",
        "confirmed": "bg-green-50 text-green-700 border border-green-100",
        "cancelled": "bg-red-50 text-red-700 border border-red-100",
        "completed": "bg-blue-50 text-blue-700 border border-blue-100"
    }

    return class_map.get(status_type, "bg-gray-100 text-gray-800")



@register.simple_tag
def get_report_status_type_color(status_type):
    """
    Returns the Tailwind class associated with a given Lab report status type.
    Usage: {% get_report_status_type_color lab_report.status %}
    """
    class_map = {
        "pending": "bg-orange-50 text-orange-700 border-orange-100",
        "normal": "bg-blue-50 text-blue-700 border border-blue-100",
        "abnormal": "bg-red-50 text-red-700 border border-red-100",
        "neutral": "bg-green-50 text-green-700 border border-green-100",
    }

    return class_map.get(status_type, "bg-gray-100 text-gray-800")



@register.simple_tag
def get_prescription_status_color(status_type):
    """
    Returns the Tailwind class associated with a given prescription status type.
    Usage: {% get_prescription_status_color prescription.status %}
    """
    class_map = {
        "active": "bg-green-50 text-green-700 border border-green-100",
        "completed": "bg-blue-50 text-blue-700 border border-blue-100",
        "discontinued": "bg-red-50 text-red-700 border border-red-100",
        "break": "bg-orange-50 text-orange-700 border border-orange-100",
    }

    return class_map.get(status_type, "bg-gray-100 text-gray-800")