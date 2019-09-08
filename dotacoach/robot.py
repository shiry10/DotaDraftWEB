from django.contrib.messages import constants as messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse

import json
import os



def index(request):
    return render(request, 'picker/index.html', {})




    # # read image path
    # module_dir = os.path.dirname(__file__)
    # file_path = os.path.join(module_dir, 'static/picker/data/hero_class.txt')
    # with open(file_path, 'r') as f:
    #     content = f.readlines()[0]
    #     hero_class = json.loads(content)
    # hero_image_paths = []
    # for c in hero_class:
    #     hero_image_paths += ['picker/images/{}.jpg'.format(hero_name) for hero_name in hero_class[c]]
    # data = {'hero_image_paths': hero_image_paths}
    #
    # # selected
    # radiant = hero_image_paths[:5]
    # dire = hero_image_paths[-5:]
    # data['radiant'] = radiant
    # data['dire'] = dire
    #
    # return render(request, 'picker/index.html', data)
