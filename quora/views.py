from django.shortcuts import render , get_object_or_404 , Http404
from .models import Question , Profile , Comment
from .forms import (LoginForm ,
                    QuestionAskForm ,
                    UserRegistrationForm ,
                    QuesUpdateForm,
                    CommentForm,
                    )
from django.contrib.auth import authenticate ,logout ,login
from django.http import HttpResponse , HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

def ques_list(request):

    ques = Question.objects.all().order_by('-id')
    context = {
        'ques' : ques
    }

    return render(request , 'quora/ques_list.html' , context = context)



def ques_detail(request,id):

    ques = get_object_or_404(Question,id=id)

    # replies = Replies.objects.all().filter(ques = ques).order_by('-id')

    is_liked = False
    if ques.likes.filter(id = request.user.id).exists():
        is_liked = True
    

    is_favourite = False
    if ques.favourite_ques.filter(id=request.user.id).exists():
        is_favourite = True

    comments =  Comment.objects.all().filter(ques = ques).order_by('-id')
    print(comments)
    for comment in comments:
        comment.is_likedd = False
        print(comment)
        if comment.likes.filter(id = request.user.id).exists():
            comment.is_likedd = True 

    if request.method == 'POST':

        if ques.restrict_comments:
            messages.success('Commenting on this post is restricted')
            return HttpResponseRedirect(reverse('quora:ques_detail',args = (id,)))

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('quora:user_login'))

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            cmnt = comment_form.save(commit=False)
            cmnt.user = request.user
            cmnt.ques = ques
            cmnt.save()
            return HttpResponseRedirect(reverse('quora:ques_detail',args = (id,)))
    else:
        comment_form  = CommentForm()

    context = {
        'q': ques,
        'is_liked' : is_liked,
        'is_favourite' : is_favourite,
        # 'is_likedd' : is_likedd,
        'likes_count' : ques.likes.count() ,
        # 'likess_count' : comments.likes.count() ,
        'comments' : comments,
        'comment_form' : comment_form ,
        # 'replies' : replies,
    }

    return render(request, 'quora/ques_detail.html', context=context)





def comment_likes(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('quora:user_login'))

    comment = get_object_or_404(Comment,id = request.POST.get('comment_id'))

    if comment.likes.filter(id = request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)

    return HttpResponseRedirect(reverse('quora:ques_detail',args=(request.POST.get('q_id'),)))


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('quora:ques_list'))

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)

            if user:

                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('quora:ques_list'))
                else:
                    return HttpResponse('User is not Active')
            else:
                return HttpResponse('User Not Available')
    else:
        form = LoginForm()

    context = {
        'form' : form
    }

    return render(request ,'quora/login.html' ,context )



@login_required()
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('quora:ques_list'))



def register(request):

    if request.user.is_authenticated:
        return HttpResponse('First logout')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user = user)
            return HttpResponseRedirect(reverse('quora:user_login'))
    else:
        form = UserRegistrationForm()

    context = {
        'form' : form
    }

    return render(request , 'quora/register.html',context)


@login_required()
def ask_question(request):

    if request.method == 'POST':
        form = QuestionAskForm(request.POST)

        if form.is_valid():
            ques = form.save(commit=False)
            ques.author = request.user
            ques.save()

            return HttpResponseRedirect(reverse('quora:ques_list'))
    else:
        form = QuestionAskForm()

    context = {
        'form' : form
    }

    return render(request , 'quora/ask_question.html',context)



@login_required()
def update_ques(request,id):

    ques = get_object_or_404(Question,id=id)
    print(ques.author)

    if ques.author != request.user:
        return Http404()

    if request.method == 'POST':
        form = QuesUpdateForm(request.POST,instance=ques)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('quora:ques_detail',args=(id,)))
    else:
        form = QuesUpdateForm(instance=ques)

    context = {
        'form' : form ,
        'ques' : ques ,
    }

    return render(request ,'quora/update_ques.html',context)



def delete_ques(request,id):

    ques = get_object_or_404(Question,id=id)

    if ques.author != request.user:
        return Http404()

    if request.method =='POST':
        ques.delete()
        return HttpResponseRedirect(reverse('quora:ques_list'))

    context = {
        'ques' : ques
    }



def delete_comment(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('quora:user_login'))

    cmnt_id = request.POST.get('comment_id')
    cmnt = get_object_or_404(Comment,id=cmnt_id)

    if cmnt.user != request.user:
        return Http404()
    cmnt.delete()
    return HttpResponseRedirect(reverse('quora:ques_detail', args=(id,)))



