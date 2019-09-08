from django.contrib.messages import constants as messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse

import json
import os
import time



def index(request):
    data = {}
    # read image path
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'static/picker/data/hero_image_paths.txt')
    with open(file_path, 'r') as f:
        content = f.readlines()[0]
        hero_image_paths = json.loads(content)
    data['hero_image_paths'] = hero_image_paths
    # hero pool order
    file_path = os.path.join(module_dir, 'static/picker/data/hero_pool_order.txt')
    with open(file_path, 'r') as f:
        content = f.readlines()[0]
        hero_pool_order = json.loads(content)['hero_pool_order']
    data['hero_pool_order'] = hero_pool_order
    # pick order
    data['pick_order'] = '0110011001'

    # selected
    radiant_heroes, dire_heroes = '', ''
    radiant_image_paths = ['picker/images/radiant_back.png'] * 5
    dire_image_paths = ['picker/images/dire_back.png'] * 5

    data['radiant_image_paths'] = radiant_image_paths
    data['dire_image_paths'] = dire_image_paths

    return render(request, 'picker/index.html', data)


def bot_select(request):
    # print(request.GET)
    bot_side = request.GET.get('bot_side')
    level = request.GET.get('level')
    pre_selected_radiant = request.GET.get('pre_selected_radiant').split(',')
    pre_selected_dire = request.GET.get('pre_selected_dire').split(',')
    round_number = request.GET.get('round_number')
    pick_order = request.GET.get('pick_order')
    if pick_order[int(round_number)] != bot_side:
        return JsonResponse({})
    time.sleep(3)
    # select hero for bot
    bot_selected_hero = ['Abaddon','Alchemist','Monkey King','Ancient Apparition','Brewmaster','Bristleback','Centaur Warrunner','Chaos Knight','Clockwerk','Doom'][int(round_number)]
    if bot_side == '0':
        pre_selected_radiant = ','.join(pre_selected_radiant + [bot_selected_hero])
    else:
        pre_selected_dire = ','.join(pre_selected_dire + [bot_selected_hero])
    # data to return to ajax
    data = {}
    data['bot_selected_hero'] = bot_selected_hero
    data['round_number'] = round_number
    data['radiant_selected'] = pre_selected_radiant
    data['dire_selected'] = pre_selected_dire
    data['bot_side'] = bot_side
    print(data)
    return JsonResponse(data)


def result(request):
    time.sleep(1)
    radiant_heroes = request.GET.get('pre_selected_radiant')
    dire_heroes = request.GET.get('pre_selected_dire')
    win_team = '0'
    print(dire_heroes, radiant_heroes)
    return JsonResponse({'win_team': win_team})



def ajax_get(request):
    cur_selected = request.GET.get('cur_selected')
    radiant_selected = request.GET.get('pre_selected_radiant', [])
    dire_selected = request.GET.get('pre_selected_dire', [])
    # radiant_selected.append(cur_selected)
    # radiant_selected = cur_selected.split(',')
    print(cur_selected, radiant_selected, dire_selected)
    data = {}
    data['radiant_selected'] = radiant_selected + ',' + cur_selected
    data['dire_selected'] = dire_selected
    radiant_image_paths = ['picker/images/radiant_back.png'] * 5
    dire_image_paths = ['picker/images/dire_back.png'] * 5
    print(data)
    return JsonResponse(data)
