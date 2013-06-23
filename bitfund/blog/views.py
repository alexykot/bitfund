from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.timezone import now
from django.template import RequestContext

from bitfund.blog.models import BlogPost, BLOGPOST_STATUS_CHOICES, BlogComment


def list(request):
    template_data = {'request': request,
                     'today': now().today(),
                     }

    blogpost_list = BlogPost.objects.filter(status=BLOGPOST_STATUS_CHOICES.published).order_by('-order')
    template_data['blogpost_list'] = blogpost_list

    return render_to_response('blog/list.djhtm', template_data, context_instance=RequestContext(request))

def post(request, slug):
    template_data = {'request': request,
                     'today': now().today(),
                     }

    blogpost = get_object_or_404(BlogPost, slug=slug)
    template_data['blogpost'] = blogpost

    blogcomments_list = BlogComment.objects.filter(blogpost_id=blogpost.id)
    template_data['blogcomments_list'] = blogcomments_list


    return render_to_response('blog/post.djhtm', template_data, context_instance=RequestContext(request))
