from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Notice, Files, Comments, MyUser, OneTimeCode
from .forms import NoticeForm, InputForm
from .filters import PostFilter


def home_view(request):
    context = {'form': InputForm()}
    if request.method == 'POST':
        form = InputForm(request.POST)
        if request.user.is_authenticated:
            logout(request)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['login'], password=form.cleaned_data['password'])
            if user is not None and user.is_active:
                login(request, user)
                return redirect('announce/')
    return render(request, 'home.html', context)


@login_required(login_url='/')
def register_code_view(request):
    if request.method == 'POST' and request.POST.get('Activate'):
        one_time_code_obj = OneTimeCode.objects.filter(
            user=request.user,
            code=request.POST.get('Activate')
        )
        if one_time_code_obj.exists():
            user_object = MyUser.objects.filter(id=request.user.id)[0]
            user_object.enabled = True
            user_object.save()
            one_time_code_obj.delete()
            return redirect('/')
    return render(request, 'account/register_code.html')


class ConfirmedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.enabled:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(register_code_view)


class NoticeCreate(LoginRequiredMixin, ConfirmedUserMixin, CreateView):
    login_url = '/'
    model = Notice
    form_class = NoticeForm
    template_name = 'announce/announce_create.html'

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            announce_obj = Notice.objects.create(
                notice_author=request.user,
                notice_title=request.POST['notice_title'],
                notice_text=request.POST['notice_text'],
                category=request.POST['category']
            )

            my_files = request.FILES.getlist('files')
            if my_files is not None and len(my_files) > 0:

                for file in my_files:
                    file_obj = Files.objects.create(
                        notice=announce_obj, name=file.name, file=file)
                    file_obj.save()

        return redirect('/notice/')


class NoticeList(ListView):
    model = Notice
    template_name = 'notice/notice.html'
    context_object_name = 'Notice'
    ordering = ['-creation_date']
    paginate_by = 10
    form_class = NoticeForm
    queryset = Notice.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NoticeDetailView(DetailView):

    model = Notice
    template_name = 'notice/notice_detail.html'
    context_object_name = 'Notice'
    queryset = Notice.objects.all()

    def get_object(self, **kwargs):
        obj = super().get_object(queryset=self.queryset)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NoticeForm()

        obj_files = Files.objects.filter(notice=self.object)
        data = []
        for file in obj_files:
            file_data = {'name': file.name,
                         'type': file.file_type}
            data.append(file_data)

        context['dataFiles'] = data

        obj_comments = Comments.objects.filter(
            notice=self.object, comment_accepted=True)
        data = []
        for comment in obj_comments:
            data.append(comment)

        context['comments'] = data

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(home_view)
        if not request.user.is_superuser:
            if not request.user.enabled:
                return redirect(register_code_view)
        obj = self.get_object()
        if request.method == 'POST':
            button_add_comment_pressed = request.POST.get("AddComment")
            if button_add_comment_pressed is not None and request.POST.get('CommentArea') != "":
                comment_obj = Comments.objects.create(
                    notice=obj, user=request.user, comment=request.POST.get('CommentArea'))
                comment_obj.save()

            return redirect('/notice/' + str(kwargs['pk']))


class NoticeUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/'
    model = Notice
    template_name = 'notice/notice_edit.html'
    form_class = NoticeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Notice_files'] = Files.objects.filter(
            notice=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        if request.method == 'POST':
            button_delete_pressed = request.POST.get("Delete")
            if button_delete_pressed is not None:
                Files.objects.filter(
                    notice=self.object,
                    file=Files.objects.get(d=int(button_delete_pressed))
                ).delete()
                return redirect('/notice/' + str(kwargs['pk']) + '/edit')
            form = NoticeForm(request.POST)
            if form.is_valid():

                self.object.notice_title = str(request.POST['notice_title'])
                self.object.notice_text = str(request.POST['notice_text'])

                files = request.FILES.getlist('files')
                for file in files:
                    file_obj = Files.objects.create(
                        notice=self.object,
                        name=file.name,
                        file=file
                    )
                    file_obj.save()

                self.object.save()
                return redirect('/notice/' + str(kwargs['pk']))
            else:
                context['form'] = NoticeForm()
        return self.render_to_response(context)


class NoticeDelete(LoginRequiredMixin, DeleteView):
    model = Notice
    login_url = '/'
    template_name = 'notice/notice_delete.html'
    success_url = "/notice/"


class NoticeComment(LoginRequiredMixin, ConfirmedUserMixin, ListView):
    login_url = '/'
    model = Comments
    template_name = 'notice/notice_comments.html'
    context_object_name = 'Comments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['AllComments'] = True
        context['myfilter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        if len(self.kwargs) > 0:
            context['Notice'] = Notice.objects.get(
                id=str(self.kwargs['pk']))
            context['AllComments'] = False
        return context

    def get_queryset(self):
        if 'announce' not in self.request.path:
            posts = Notice.objects.filter(notice_author=self.request.user)
            queryset = Comments.objects.filter(notice__in=posts, comment_accepted=False)
        else:
            queryset = Comments.objects.filter(
                notice=Notice.objects.get(id=str(self.kwargs['pk'])),
                comment_accepted=False
            )
        return queryset

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            pk = None
            button_accept_pressed = request.POST.get('Accept')
            button_denied_pressed = request.POST.get('Denied')
            if button_accept_pressed is not None:
                obj_comment = Comments.objects.get(id=button_accept_pressed)
                obj_comment.comment_accepted = True
                obj_comment.save()
                pk = obj_comment.notice_id
            elif button_denied_pressed is not None:
                obj_comment = Comments.objects.get(id=button_denied_pressed)
                pk = obj_comment.notice_id
                obj_comment.delete()

            if pk is not None:
                return redirect('/notice/' + str(pk) + "/comments")
            return redirect('/notice/' + str(kwargs['pk']) + "/comments")
