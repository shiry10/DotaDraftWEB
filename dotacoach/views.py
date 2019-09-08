from django.contrib.messages import constants as messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from dotacoach.models import NameId, WinrateOne, WinrateSingle
from dotacoach.pickers import Random_picker, Greedy_picker, Monte_Carlo_picker

import json
import os
import time
from keras.models import load_model
from keras import backend as K
import numpy as np



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
    pre_selected_radiant = request.GET.get('pre_selected_radiant')
    pre_selected_dire = request.GET.get('pre_selected_dire')
    round_number = int(request.GET.get('round_number'))
    pick_order = request.GET.get('pick_order')
    # select hero for bot
    bot_selected_heroes = []
    while round_number < 10 and pick_order[round_number] == bot_side:
        cur_selected = bot_select_single(round_number, bot_side, pre_selected_radiant, pre_selected_dire, pick_order, level)
        bot_selected_heroes.append(cur_selected)
        if bot_side == '0':
            pre_selected_radiant += ',' + cur_selected
        else:
            pre_selected_dire += ',' + cur_selected
        round_number += 1
    # data to return to ajax
    data = {}
    data['bot_selected_heroes'] = bot_selected_heroes
    data['round_number'] = round_number
    data['radiant_selected'] = pre_selected_radiant
    data['dire_selected'] = pre_selected_dire
    data['bot_side'] = bot_side
    data['bot_selected_heroes_images'] = ["/static/picker/images/hero_grey/{}.jpg".format(hero) for hero in bot_selected_heroes]
    print(data)
    return JsonResponse(data)


def bot_select_single(round_number, bot_side, pre_selected_radiant, pre_selected_dire, pick_order, level):
    picked_names_radiant = pre_selected_radiant.split(',')[1:]
    picked_names_dire = pre_selected_dire.split(',')[1:]
    picked_ids_radiant = [NameId.objects.filter(name=name)[0].id for name in picked_names_radiant]
    picked_ids_dire = [NameId.objects.filter(name=name)[0].id for name in picked_names_dire]
    side_map = {'0':'Radiant', '1':'Dire'}
    # select hero (id) according different hard level
    if level == 'easy':
        time.sleep(1)
        picker = Random_picker(side=side_map[bot_side])
        cur_picked_id = picker.pick(Round=round_number, picked_r=picked_ids_radiant, picked_d=picked_ids_dire)
    if level == 'medium':
        time.sleep(1)
        picker = Greedy_picker(side=side_map[bot_side])
        cur_picked_id = picker.pick(Round=round_number, picked_r=picked_ids_radiant, picked_d=picked_ids_dire)
    if level == 'hard':
        t0 = time.time()
        picker = Monte_Carlo_picker(side=side_map[bot_side])
        cur_picked_id = picker.pick(Round=round_number, picked_r=picked_ids_radiant, picked_d=picked_ids_dire, Max_sampling=1500)
        print('time: ', time.time()-t0)
    if level == 'crazy':
        t0 = time.time()
        picker = Monte_Carlo_picker(side=side_map[bot_side])
        cur_picked_id = picker.pick(Round=round_number, picked_r=picked_ids_radiant, picked_d=picked_ids_dire, Max_sampling=7500)
        print('time: ', time.time()-t0)
    # map name to id
    cur_picked_name = NameId.objects.filter(id=cur_picked_id)[0].name
    return cur_picked_name



def result(request):
    radiant_heroes = request.GET.get('pre_selected_radiant')
    dire_heroes = request.GET.get('pre_selected_dire')
    win_team = predict(radiant_heroes, dire_heroes)
    return JsonResponse({'win_team': win_team})



def predict(radiant_heroes, dire_heroes):
    time.sleep(2)
    # load predictor
    K.clear_session()
    module_dir = os.path.dirname(__file__)
    model_path = os.path.join(module_dir, 'static/picker/data/predictor.h5')
    predictor = load_model(model_path)
    # formulate lineup
    radiant_names = radiant_heroes.split(',')[1:]
    radiant_ids = [NameId.objects.filter(name=name)[0].id for name in radiant_names]
    dire_names = dire_heroes.split(',')[1:]
    dire_ids = [NameId.objects.filter(name=name)[0].id for name in dire_names]
    lineup = np.array(radiant_ids + dire_ids).reshape(1, 10)
    win_probability = predictor.predict(lineup)
    K.clear_session()
    print('\n', lineup, win_probability)
    win_team = '0' if win_probability > 0.5 else '1'
    return win_team
