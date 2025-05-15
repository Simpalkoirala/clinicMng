from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.simple_tag
def get_svg_icon(action ):
    """
    Returns the Svg Icon code with a given action type type.
    Usage: {% get_svg_icon activity.action %}
    """
    class_map = {
        "UPLOAD_DOC": """
<svg class="w-4 h-4 text-blue-500" viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
    <g transform="matrix(0.83 0 0 0.83 12 12)" >
        <g transform="matrix(1 0 0 1 -4 0)" >
            <path style=" stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: currentColor; fill-rule: nonzero; opacity: 1;" transform=" translate(-8, -12)" d="M 4 9 L 12 9 L 12 11 L 4 11 z M 4 13 L 10 13 L 10 15 L 4 15 z" stroke-linecap="round" />
        </g>
        <g transform="matrix(1 0 0 1 -0.15 0)" >
            <path style=" stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: currentColor; fill-rule: nonzero; opacity: 1;" transform=" translate(-11.85, -12)" d="M 16 6 L 16 11 L 18 11 L 18 4.586 L 13.414 0 L 2 0 C 0.8954305003384131 0 0 0.8954305003384131 0 2 L 0 20 C 0 21.104569499661586 0.8954305003384131 22 2 22 L 12 22 L 12 20 L 2 20 L 2 2 L 12 2 L 12 6 z M 19 14.585 L 14.293 19.292 L 15.706999999999999 20.706000000000003 L 18 18.413 L 18 24 L 20 24 L 20 18.413 L 22.293 20.706 L 23.707 19.291999999999998 L 19 14.585 z" stroke-linecap="round" />
        </g>
    </g>
</svg>
""",
        
        "DELETE_DOC": """
<svg class="w-4 h-4 text-blue-500" viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'>
    <g transform="matrix(0.83 0 0 0.83 12 12)" >
        <g style="" >
            <g transform="matrix(1 0 0 1 5.25 5.25)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-17.25, -17.25)" d="M 11.25 17.25 C 11.25 20.56370849898476 13.936291501015239 23.25 17.25 23.25 C 20.56370849898476 23.25 23.25 20.56370849898476 23.25 17.25 C 23.25 13.936291501015239 20.56370849898476 11.25 17.25 11.25 C 13.936291501015239 11.25 11.25 13.936291501015239 11.25 17.25 Z" stroke-linecap="round" />
            </g>
            <g transform="matrix(1 0 0 1 5.25 5.25)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-17.25, -17.25)" d="M 19.5 15 L 15 19.5" stroke-linecap="round" />
            </g>
            <g transform="matrix(1 0 0 1 5.25 5.25)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-17.25, -17.25)" d="M 15 15 L 19.5 19.5" stroke-linecap="round" />
            </g>
            <g transform="matrix(1 0 0 1 -3.88 -2.25)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-8.12, -9.75)" d="M 8.25 14.25 C 5.958521517472274 14.25018067231152 4.032850232000278 12.528401334692077 3.777641201877387 10.251178899471094 C 3.5224321717544953 7.9739564642501115 5.019197791218794 5.868623552918917 7.253869433269345 5.3615571659978905 C 9.488541075319896 4.854490779076864 11.74737661338783 6.107645198574303 12.5 8.272000000000002" stroke-linecap="round" />
            </g>
            <g transform="matrix(1 0 0 1 -3 -3)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-9, -9)" d="M 9.75 9.75 L 8.25 9.75 L 8.25 8.25" stroke-linecap="round" />
            </g>
            <g transform="matrix(1 0 0 1 -3 -1.5)" >
                <path style="stroke: currentColor; stroke-width: 2; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-9, -10.5)" d="M 7.5 20.25 L 2.25 20.25 C 1.4215728752538097 20.25 0.75 19.57842712474619 0.75 18.75 L 0.75 2.25 C 0.75 1.4215728752538097 1.4215728752538097 0.75 2.25 0.75 L 12.879 0.75 C 13.276690700618996 0.7503501040797631 13.657965283433596 0.9086150252480875 13.939 1.1900000000000004 L 16.811 4.061 C 17.092263236672398 4.3424434712249935 17.250180275391664 4.724106291455379 17.25 5.121999999999998 L 17.25 7.5" stroke-linecap="round" />
            </g>
        </g>
    </g>
</svg>
""",
        
        "BOOK_APPT": """
<svg class="w-4 h-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M8 2v4 M16 2v4"></path>
    <rect width="18" height="18" x="3" y="4" rx="2"></rect>
    <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18"></path>
</svg>
""",
        
        "CANCEL_APPT": """
<svg class="w-4 h-4 text-blue-500" viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><rect width='24' height='24' stroke='none' fill='#000000' opacity='0'/>
    <g transform="matrix(0.77 0 0 0.77 12 12)" >
        <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: currentColor; fill-rule: nonzero; opacity: 1;" transform=" translate(-16, -16)" d="M 16 3 C 8.832031 3 3 8.832031 3 16 C 3 23.167969 8.832031 29 16 29 C 23.167969 29 29 23.167969 29 16 C 29 8.832031 23.167969 3 16 3 Z M 16 5 C 22.085938 5 27 9.914063 27 16 C 27 22.085938 22.085938 27 16 27 C 9.914063 27 5 22.085938 5 16 C 5 9.914063 9.914063 5 16 5 Z M 12.21875 10.78125 L 10.78125 12.21875 L 14.5625 16 L 10.78125 19.78125 L 12.21875 21.21875 L 16 17.4375 L 19.78125 21.21875 L 21.21875 19.78125 L 17.4375 16 L 21.21875 12.21875 L 19.78125 10.78125 L 16 14.5625 Z" stroke-linecap="round" />
    </g>
</svg>
 """,

        "DOC": """
<svg class="w-4 h-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round"
        d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z M14 2v4a2 2 0 0 0 2 2h4 M10 9H8 M16 13H8 M16 17H8">
    </path>
</svg>
""",

        "MESSAGE": """
<svg class="w-4 h-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round"
        d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z">
    </path>
</svg>
"""
    }

    return mark_safe(class_map.get(action, ""))