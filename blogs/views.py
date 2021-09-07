from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail


class PostListView(ListView):
    model = Post
    paginate_by = 1


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create Comment object but don't save to database yet.
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment.
            new_comment.post = post
            # Save the commit to the database.
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'blogs/detail.html', {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form})


def post_share(request, post_id):
    # Retrive post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read" f"{post.title}"
            message = f"Read{post.title} at {post_url}\n\n" f"{cd['name']}\s comments: {cd['comments']}"
            send_mail(subject, message, 'cromarties2913@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blogs/share.html', {'post': post, 'form': form, 'sent': sent})
