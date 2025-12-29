
from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required

# from youtubesearchpython import VideosSearch
from youtube_search import YoutubeSearch
import requests
import wikipedia

def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method=="POST":
        form=NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes added from {request.user.username} successfully")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)   # show ALL notes from admin
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)



@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect ("notes")


class NotesDetailView(generic.DetailView):
    model=Notes

# def homeee(request):
#     return render(request,'dashboard/homework.html')

@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is finished']
                if finished =='on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks=Homework(user=request.user,subject=request.POST['subject'],title=request.POST['title'],description=request.POST['description'],due=request.POST['due'],is_finished= finished)
            homeworks.save()
            messages.success(request,f"Homework added from {request.user.username}")
    else:
        form=HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context={'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,"dashboard/homework.html",context)

@login_required
def update_homework(request,pk=None):
    homework= Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

from youtubesearchpython import VideosSearch

# def youtube(request):
#     if request.method == "POST":
#         form = DashboardForm(request.POST)
#         text = request.POST['text']

#         # Search YouTube
#         video = VideosSearch(text, limit=10)
#         result_list = []

#         for i in video.result()['result']:
#             result_dict = {
#                 'input': text,
#                 'title': i.get('title'),
#                 'duration': i.get('duration'),
#                 'thumbnail': i['thumbnails'][0]['url'],
#                 'channel': i['channel']['name'],
#                 'link': i['link'],
#                 'viewcount': i['viewCount']['short'],
#                 'published': i.get('publishedTime'),
#             }

#             # description snippet
#             desc = ''
#             if i.get('descriptionSnippet'):
#                 for j in i['descriptionSnippet']:
#                     desc += j['text']

#             result_dict['description'] = desc
#             result_list.append(result_dict)

#         context = {
#             'form': form,
#             'results': result_list
#         }
#         return render(request, 'dashboard/youtube.html', context)

#     else:
#         form = DashboardForm()

#     context = {'form': form}
#     return render(request, 'dashboard/youtube.html', context)


def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']

        results = YoutubeSearch(text, max_results=15).to_dict()

        result_list = []

        for i in results:
            result_dict = {
                'input': text,
                'title': i.get('title'),
                'duration': i.get('duration'),
                'thumbnail': i['thumbnails'][0],            # image
                'channel': i.get('channel'),
                'link': 'https://www.youtube.com' + i.get('url_suffix'),
                'viewcount': i.get('views'),
                'published': i.get('publish_time'),
                'description': i.get('long_desc', ''),
            }

            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/youtube.html', context)

    form = DashboardForm()
    return render(request, 'dashboard/youtube.html', {'form': form})


@login_required
def todo(request):
    form = TodoFrom()   # form must always be created first

    if request.method == "POST":
        form = TodoFrom(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get("is_finished")
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            # this must be outside the except block
            todos = Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todos.save()

            messages.success(request, f"Todo added from {request.user.username}!!")

        else:
            form = TodoFrom()  # re-create form if invalid

    # your existing code (only variable renamed for clarity)
    todo = Todo.objects.filter(user=request.user)

    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False

    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done
    }

    return render(request, "dashboard/todo.html", context)

@login_required
def update_todo(request,pk=None):
    todo =Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished= True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

# this is book sections
def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']

        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)   # ✅ FIXED
        answer = r.json()

        result_list = []

        for i in range(10):
            volume = answer['items'][i]['volumeInfo']

            result_dict = {
                'title': volume.get('title'),
                'subtitle': volume.get('subtitle'),
                'description': volume.get('description'),
                'count': volume.get('pageCount'),
                'categories': volume.get('categories'),
                'rating': volume.get('averageRating'),
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
                'preview': volume.get('previewLink'),
            }

            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/books.html', context)

    else:
        form = DashboardForm()

    return render(request, 'dashboard/books.html', {'form': form})


# def dictionary(request):
#     if request.method == 'POST':
#         form=DashboardForm(request.POST)
#         text =request.POST['text']
#         url="https://abi.distionaryapi.dev/api/v2/entries/en_US/"+text
#         r= request.get(url)
#         answer =r.json()
#         try:
#             phonetics=answer[0]['phonetics'][0]['text']
#             audio=answer[0]['phonetics'][0]['audio']
#             defination=answer[0]['meanings'][0]['definations'][0]['defination']
#             example=answer[0]['meanings'][0]['definations'][0]['example']
#             synonyms=answer[0]['meanings'][0]['definations'][0]['synonyms']
#             context ={'form':form,'input':text,'phonetics':phonetics,'audio':audio,'defination':defination,'example':example,'synonyms':synonyms}
#         except:
#              context ={'form':form,'input':''}
#         return render(request,"dashboard/dictionary.html",context)
#     else:
#         form=DashboardForm()
#         context={'form':form}
    # return render(request,'dashboard/dictionary.html',context)


def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']

        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + text
        r = requests.get(url)
        answer = r.json()

        try:
            phonetics = answer[0]['phonetics'][0].get('text')
            audio = answer[0]['phonetics'][0].get('audio')
            definition = answer[0]['meanings'][0]['definitions'][0].get('definition')
            example = answer[0]['meanings'][0]['definitions'][0].get('example')

            # ✅ FIX: collect synonyms properly
            synonyms = set()
            for meaning in answer[0]['meanings']:
                for defi in meaning['definitions']:
                    for syn in defi.get('synonyms', []):
                        synonyms.add(syn)

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': list(synonyms)  # convert set to list
            }

        except Exception:
            context = {
                'form': form,
                'input': text
            }

        return render(request, "dashboard/dictionary.html", context)

    else:
        form = DashboardForm()

    return render(request, 'dashboard/dictionary.html', {'form': form})


def  wiki(request):
    if request.method == "POST":
        text=request.POST['text']
        form = DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'detail':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
        context={'form':form,'input':False}
    return render(request,'dashboard/wiki.html',context)


# def conversion(request):
#     if request.method == 'POST':
#         form=ConversionForm(request.POST)
#         if request.POST['measurement']=='length':
#             measurement_form=conversionLengthForm()
#             context={'form':form,'m_form':measurement_form,'input':True}
#             if 'input' in request.POST:
#                 first=request.POST['measure1']
#                 second=request.POST['measure2']
#                 input=request.POST['input']
#                 answer=''
#                 if input and int(input)>=0:
#                     if first=='yard' and second=='foot':
#                         answer=f"{input}yard={int(input)*3}foot"
                    
#                     if first=='foot' and second=='yard':
#                         answer=f"{input}foot={int(input)/3}yard"
#                 context={'form':form,'m_form':measurement_form,'input':True,'answer':answer}
#         if request.POST['measurement']=='mass':
#             measurement_form=conversionLMassForm()
#             context={'form':form,'m_form':measurement_form,'input':True}
#             if 'input' in request.POST:
#                 first=request.POST['measure1']
#                 second=request.POST['measure2']
#                 input=request.POST['input']
#                 answer=''
#                 if input and int(input)>=0:
#                     if first=='pound' and second=='kilogram':
#                         answer=f"{input}pound={int(input)*0.453592}kilogram"
                    
#                     if first=='kilogram' and second=='pound':
#                         answer=f"{input}kilogram={int(input)*2.20462}pound"
#                 context={'form':form,'m_form':measurement_form,'input':True,'answer':answer}
                       
#         else:
#             form =ConversionForm()
#             context ={'form':form,'input':False}
#         return render(request,'dashboard/conversion.html',context)

def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)

        if request.POST['measurement'] == 'length':
            measurement_form = conversionLengthForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}

            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                value = request.POST['input']
                answer = ''

                if value and int(value) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f"{value} yard = {int(value) * 3} foot"

                    if first == 'foot' and second == 'yard':
                        answer = f"{value} foot = {int(value) / 3} yard"

                context['answer'] = answer

            return render(request, 'dashboard/conversion.html', context)

        elif request.POST['measurement'] == 'mass':
            measurement_form = conversionLMassForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}

            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                value = request.POST['input']
                answer = ''

                if value and int(value) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f"{value} pound = {int(value) * 0.453592} kilogram"

                    if first == 'kilogram' and second == 'pound':
                        answer = f"{value} kilogram = {int(value) * 2.20462} pound"

                context['answer'] = answer

            return render(request, 'dashboard/conversion.html', context)

    # ✅ THIS PART FIXES THE ERROR
    form = ConversionForm()
    context = {'form': form, 'input': False}
    return render(request, 'dashboard/conversion.html', context)


# def register(request):
#     if request.method == 'POST':
#         form=UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username=form.cleaned_data.get('username')
#             messages.success(request,f"Account Created for {username} !!")
#     else:
#         form=UserRegistrationForm()
#     context={
#         'form':form
#     }   
#     return render(request,'dashboard/register.html',context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account Created for {username} !!")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'dashboard/register.html', {'form': form})


@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    todos=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todos)==0:
        todos_done=True
    else:
        todos_done=False
    context={
        'homeworks':homeworks,
        'todos': todos,
        'homework_done':homework_done,
        'todos_done':todos_done

    }
    return render(request,'dashboard/profile.html',context)
